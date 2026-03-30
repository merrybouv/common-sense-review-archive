"""
02_analyze_themes.py
====================
Common Sense Education Review Archive — Step 2 of 3
Meredith Bouvier, PhD | NET Lab, Inc.

PURPOSE
-------
Sends critical reviews (output of 01_score_reviews.py) to the Claude API
for structured thematic analysis, one API call per platform. Results are
saved as JSON files, one per platform, plus a combined file.

THIS STEP COSTS MONEY (~$1-2 total for all 7 platforms).
Estimated: 7 API calls x ~2,000 tokens each = ~$0.50-2.00 depending on
review volume. Each platform's JSON is saved immediately after its call
completes — if the script errors partway through, completed platforms
are not lost.

INPUTS
------
    outputs/critical_reviews.csv    output of 01_score_reviews.py

OUTPUTS
-------
    outputs/themes_[platform].json  structured analysis per platform
    outputs/themes_all.json         all platforms combined

WHAT THE ANALYSIS RETURNS (per platform)
-----------------------------------------
    themes              list of concern themes, each with:
                          label         short descriptive name
                          description   2-3 sentences grounded in review text
                          quotes        1-2 short illustrative quotes
                          raised_by     teachers / parents / students
    student_voice       reviews that appear written by students directly
    emotional_register  overall tone of the critical reviews
    mandatory_context   whether platform use appears required or voluntary
    practitioner_terms  vocabulary used that differs from academic language

USAGE
-----
    # requires ANTHROPIC_API_KEY in environment
    export ANTHROPIC_API_KEY=your_key_here

    # from analysis_pipeline directory with netlab_env activated:
    python 02_analyze_themes.py

    # analyze one platform only (useful for testing before full run):
    python 02_analyze_themes.py --platform iReady

    # custom input file or output directory:
    python 02_analyze_themes.py --input outputs/critical_reviews.csv --output_dir outputs

DEPENDENCIES
------------
    pandas
    anthropic

    pip install pandas anthropic

CITATION
--------
    Bouvier, M. (2026). Common Sense Education Community Review Archive.
    Open Science Framework. https://osf.io/ehbfv/
    Code: https://github.com/merrybouv/common-sense-review-archive
"""

import os
import json
import argparse
import time
import pandas as pd
import anthropic


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

MODEL = "claude-opus-4-5"  # use Opus for best thematic analysis quality
MAX_TOKENS = 2000

SYSTEM_PROMPT = """You are analyzing community reviews flagged as critical of EdTech platforms.
These reviews were collected from Common Sense Education in February 2026 before being removed
from public access. Reviewers include teachers, parents, and students writing in their own voice.

Your task is to produce a structured thematic analysis of the concerns expressed across the
provided reviews for a single platform. Be precise and grounded in the actual review text.
Do not editorialize beyond what reviewers say.

For each theme you identify:
- Give it a clear, descriptive label
- Describe the concern in 2-3 sentences using the reviewers' own framing
- Select 1-2 short illustrative quotes (under 20 words each)
- Note who raises this concern: teachers, parents, and/or students

Additionally note:
- Any reviews that appear to be written by students in their own voice (not teachers
  or parents reporting on students) — this is significant and should be flagged explicitly
- The overall emotional register of the reviews (e.g. matter-of-fact, desperate, angry,
  resigned, alarmed)
- Whether platform use appears mandatory (assigned by school/district) or voluntary
- Vocabulary the reviewers use that differs from academic EdTech research language
  (e.g. "crying", "stress machine", "dread" vs academic terms like "disengagement")

Respond ONLY with valid JSON matching this exact structure — no preamble, no markdown fences:

{
  "platform": "...",
  "review_count": N,
  "themes": [
    {
      "label": "...",
      "description": "...",
      "quotes": ["...", "..."],
      "raised_by": ["teachers", "parents", "students"]
    }
  ],
  "student_voice": {
    "present": true or false,
    "count": N,
    "notes": "brief description of student-authored reviews if present"
  },
  "emotional_register": "...",
  "mandatory_context": "...",
  "practitioner_terms": ["term1", "term2", "..."]
}"""


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def build_user_message(platform: str, reviews: pd.DataFrame) -> str:
    """Format reviews for the API prompt."""
    lines = [f"Analyze these {len(reviews)} critical reviews of {platform}:\n"]
    for i, (_, row) in enumerate(reviews.iterrows(), 1):
        my_take = str(row.get("my_take", "")).strip()
        how_i_use = str(row.get("how_i_use_it", "")).strip()
        text = my_take
        if how_i_use and how_i_use.lower() not in ("nan", ""):
            text += f"\n[How I use it: {how_i_use[:200]}]"
        lines.append(
            f"[Review {i}] Score: {row.get('concern_score', '?')} | "
            f"{row.get('date_posted', '')}\n"
            f"Title: {row.get('review_title', row.get('title', '(no title)'))}\n"
            f"{text[:1200]}"
        )
    return "\n\n---\n\n".join(lines)


def analyze_platform(client: anthropic.Anthropic, platform: str, reviews: pd.DataFrame) -> dict:
    """
    Send one platform's critical reviews to the API and return parsed JSON.

    Retries once on failure with a 10-second pause.
    """
    print(f"\n  Sending {len(reviews)} reviews for {platform}...")
    user_message = build_user_message(platform, reviews)

    for attempt in range(2):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_message}]
            )
            raw = response.content[0].text.strip()

            # Strip markdown fences if model adds them despite instructions
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            result = json.loads(raw)

            # Log token usage
            usage = response.usage
            print(f"  Done. Tokens used: {usage.input_tokens} in / {usage.output_tokens} out")
            return result

        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {attempt+1}): {e}")
            if attempt == 0:
                print("  Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print(f"  Failed to parse response for {platform}. Saving raw text.")
                return {"platform": platform, "error": "JSON parse failed", "raw": raw}

        except anthropic.APIError as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            if attempt == 0:
                print("  Retrying in 10 seconds...")
                time.sleep(10)
            else:
                return {"platform": platform, "error": str(e)}

    return {"platform": platform, "error": "Unknown failure"}


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(input_file: str, output_dir: str, platform_filter: str | None):

    print(f"\n{'='*60}")
    print("02_analyze_themes.py — Common Sense Education Review Archive")
    print(f"{'='*60}")
    print(f"Input file  : {input_file}")
    print(f"Output dir  : {output_dir}")
    print(f"Model       : {MODEL}")
    if platform_filter:
        print(f"Platform    : {platform_filter} (single platform mode)")

    # Check API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY not found in environment.\n"
            "Run: export ANTHROPIC_API_KEY=your_key_here"
        )

    # Load critical reviews
    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Run 01_score_reviews.py first."
        )

    df = pd.read_csv(input_file)
    print(f"\nLoaded {len(df)} critical reviews from {input_file}")

    # Filter to one platform if requested
    platforms = sorted(df["platform"].unique())
    if platform_filter:
        if platform_filter not in platforms:
            raise ValueError(
                f"Platform '{platform_filter}' not found.\n"
                f"Available: {', '.join(platforms)}"
            )
        platforms = [platform_filter]

    print(f"Platforms to analyze: {', '.join(platforms)}")
    print(f"\nEstimated cost: ${len(platforms) * 0.20:.2f}–${len(platforms) * 0.40:.2f} "
          f"({len(platforms)} API calls)")
    print("\nNote: Each platform saves immediately — partial runs are not lost.")

    # Initialize client
    client = anthropic.Anthropic(api_key=api_key)
    os.makedirs(output_dir, exist_ok=True)

    all_results = []
    total_input_tokens = 0
    total_output_tokens = 0

    for platform in platforms:
        platform_reviews = df[df["platform"] == platform].copy()
        print(f"\n[{platforms.index(platform)+1}/{len(platforms)}] {platform} — {len(platform_reviews)} reviews")

        result = analyze_platform(client, platform, platform_reviews)
        all_results.append(result)

        # Save immediately
        safe_name = platform.lower().replace(" ", "_")
        out_path = os.path.join(output_dir, f"themes_{safe_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"  Saved: {out_path}")

        # Brief pause between calls to be respectful to the API
        if platform != platforms[-1]:
            time.sleep(2)

    # Save combined file
    combined_path = os.path.join(output_dir, "themes_all.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nSaved combined: {combined_path}")

    # Summary
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    for result in all_results:
        if "error" in result:
            print(f"  {result['platform']:<22} ERROR: {result['error']}")
        else:
            n_themes = len(result.get("themes", []))
            sv = result.get("student_voice", {})
            sv_flag = " *** STUDENT VOICE PRESENT ***" if sv.get("present") else ""
            print(f"  {result['platform']:<22} {n_themes} themes | "
                  f"register: {result.get('emotional_register', '?')[:40]}{sv_flag}")

    print(f"\nDone. Run 03_summary_report.py next.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Thematic analysis of critical CSM reviews via Claude API."
    )
    parser.add_argument(
        "--input",
        default="outputs/critical_reviews.csv",
        help="Path to critical_reviews.csv from step 01 (default: outputs/critical_reviews.csv)"
    )
    parser.add_argument(
        "--output_dir",
        default="outputs",
        help="Directory for JSON output files (default: outputs/)"
    )
    parser.add_argument(
        "--platform",
        default=None,
        help="Analyze one platform only, e.g. --platform iReady (default: all platforms)"
    )
    args = parser.parse_args()
    main(args.input, args.output_dir, args.platform)
