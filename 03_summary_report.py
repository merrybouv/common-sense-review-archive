"""
03_summary_report.py
====================
Common Sense Education Review Archive — Step 3 of 3
Meredith Bouvier, PhD | NET Lab, Inc.

PURPOSE
-------
Reads the per-platform theme JSON files produced by 02_analyze_themes.py
and generates a structured markdown summary report across all platforms.

Outputs a single markdown file suitable for inclusion as a paper appendix
or supplementary material, plus a plain-text console summary.

INPUTS
------
    outputs/themes_*.json       per-platform analysis from step 02
    outputs/critical_reviews.csv  scored reviews from step 01

OUTPUTS
-------
    outputs/summary_report.md   full cross-platform findings report

USAGE
-----
    # from analysis_pipeline directory with netlab_env activated:
    python 03_summary_report.py

    # custom output directory:
    python 03_summary_report.py --output_dir outputs

DEPENDENCIES
------------
    pandas, json
    (no API calls, no internet required)

CITATION
--------
    Bouvier, M. (2026). Common Sense Education Community Review Archive.
    Open Science Framework. https://osf.io/ehbfv/
    Code: https://github.com/merrybouv/common-sense-review-archive
"""

import os
import json
import glob
import argparse
from datetime import datetime
import pandas as pd


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def load_theme_files(output_dir: str) -> list[dict]:
    """Load all themes_*.json files, skipping themes_all.json."""
    pattern = os.path.join(output_dir, "themes_*.json")
    files = sorted(glob.glob(pattern))
    files = [f for f in files if "themes_all" not in f]

    if not files:
        raise FileNotFoundError(
            f"No themes_*.json files found in '{output_dir}'.\n"
            "Run 02_analyze_themes.py first."
        )

    results = []
    for filepath in files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "error" in data:
            print(f"  Warning: {os.path.basename(filepath)} contains an error, skipping.")
            continue
        results.append(data)
        print(f"  Loaded: {os.path.basename(filepath)}")

    return results


def load_scored_reviews(output_dir: str) -> pd.DataFrame | None:
    """Load critical_reviews.csv for corpus statistics."""
    path = os.path.join(output_dir, "critical_reviews.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def format_raised_by(raised_by: list[str]) -> str:
    """Format raised_by list as a readable string."""
    if not raised_by:
        return "unspecified"
    return ", ".join(raised_by)


# ---------------------------------------------------------------------------
# REPORT BUILDER
# ---------------------------------------------------------------------------

def build_report(results: list[dict], df_critical: pd.DataFrame | None) -> str:
    """Build the full markdown report as a string."""

    lines = []
    now = datetime.now().strftime("%B %d, %Y")

    # Header
    lines += [
        "# Common Sense Education Review Archive — Thematic Analysis Report",
        "",
        f"**Generated:** {now}  ",
        "**Maintainer:** Meredith Bouvier, PhD | NET Lab, Inc.  ",
        "**Dataset:** https://osf.io/ehbfv/  ",
        "**Pipeline:** https://github.com/merrybouv/common-sense-review-archive  ",
        "",
        "---",
        "",
    ]

    # Corpus overview
    lines += [
        "## Corpus Overview",
        "",
    ]

    if df_critical is not None:
        total_critical = len(df_critical)
        by_platform = df_critical.groupby("platform").size().reset_index(name="critical_reviews")
        lines += [
            f"Critical reviews analyzed (concern score ≥ 2): **{total_critical}**  ",
            f"Platforms: **{len(results)}**  ",
            "",
            "| Platform | Critical Reviews |",
            "|---|---|",
        ]
        for _, row in by_platform.iterrows():
            lines.append(f"| {row['platform']} | {row['critical_reviews']} |")
        lines.append("")
    else:
        lines += [
            f"Platforms analyzed: {len(results)}",
            "",
        ]

    # Student voice summary — pull this up high, it's the key finding
    sv_platforms = [r for r in results if r.get("student_voice", {}).get("present")]
    if sv_platforms:
        lines += [
            "## Student Voice",
            "",
            "The following platforms have reviews that appear to be written by students "
            "in their own voice — not teachers or parents reporting on student experience. "
            "This is a significant finding: these voices are now inaccessible following "
            "the removal of community reviews from Common Sense Education product pages.",
            "",
        ]
        for r in sv_platforms:
            sv = r.get("student_voice", {})
            lines += [
                f"**{r['platform']}**  ",
                f"{sv.get('notes', '')}",
                "",
            ]
        lines += ["---", ""]

    # Per-platform analysis
    lines += [
        "## Per-Platform Thematic Analysis",
        "",
    ]

    for r in sorted(results, key=lambda x: x.get("platform", "")):
        platform = r.get("platform", "Unknown")
        review_count = r.get("review_count", "?")
        emotional_register = r.get("emotional_register", "not recorded")
        mandatory_context = r.get("mandatory_context", "not recorded")
        practitioner_terms = r.get("practitioner_terms", [])
        themes = r.get("themes", [])
        sv = r.get("student_voice", {})

        lines += [
            f"### {platform}",
            "",
            f"**Reviews analyzed:** {review_count}  ",
            f"**Emotional register:** {emotional_register}  ",
            f"**Mandatory context:** {mandatory_context}  ",
        ]

        if sv.get("present"):
            lines.append(f"**Student voice present:** Yes — {sv.get('notes', '')}  ")

        lines.append("")

        if practitioner_terms:
            terms_str = ", ".join(f"`{t}`" for t in practitioner_terms)
            lines += [
                f"**Practitioner vocabulary:** {terms_str}",
                "",
            ]

        if themes:
            lines.append("**Themes:**")
            lines.append("")
            for i, theme in enumerate(themes, 1):
                label = theme.get("label", "Unlabeled")
                description = theme.get("description", "")
                quotes = theme.get("quotes", [])
                raised_by = theme.get("raised_by", [])

                lines += [
                    f"**{i}. {label}**  ",
                    f"*Raised by: {format_raised_by(raised_by)}*  ",
                    "",
                    description,
                    "",
                ]

                for quote in quotes:
                    lines.append(f"> \"{quote}\"")
                lines.append("")
        else:
            lines += ["*No themes recorded.*", ""]

        lines += ["---", ""]

    # Cross-platform summary table
    lines += [
        "## Cross-Platform Summary",
        "",
        "| Platform | Themes | Student Voice | Emotional Register | Mandatory? |",
        "|---|---|---|---|---|",
    ]

    for r in sorted(results, key=lambda x: x.get("platform", "")):
        platform = r.get("platform", "?")
        n_themes = len(r.get("themes", []))
        sv_present = "Yes" if r.get("student_voice", {}).get("present") else "No"
        register = r.get("emotional_register", "?")[:50]
        mandatory = r.get("mandatory_context", "?")[:60]
        lines.append(f"| {platform} | {n_themes} | {sv_present} | {register} | {mandatory} |")

    lines += [
        "",
        "---",
        "",
        "## Methodological Notes",
        "",
        "Reviews were identified as critical using a lexical concern vocabulary index "
        "(77 terms across 7 categories) applied in `01_score_reviews.py`. A threshold "
        "of score ≥ 2 was used to identify substantive concern. Thematic analysis was "
        "conducted via the Claude API (`02_analyze_themes.py`). All code and the full "
        "scored corpus are available at the repository linked above.",
        "",
        "The 619-review corpus is a purposive, not random, sample. Platforms were "
        "selected based on prevalence in K-12 schools. Reviews were collected in "
        "February 2026. Community reviews are no longer accessible on Common Sense "
        "Education product pages as of March 2026.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(output_dir: str):

    print(f"\n{'='*60}")
    print("03_summary_report.py — Common Sense Education Review Archive")
    print(f"{'='*60}")
    print(f"Output directory: {output_dir}")

    print("\nLoading theme files...")
    results = load_theme_files(output_dir)
    print(f"Loaded {len(results)} platform analyses")

    df_critical = load_scored_reviews(output_dir)
    if df_critical is not None:
        print(f"Loaded critical_reviews.csv ({len(df_critical)} reviews)")
    else:
        print("critical_reviews.csv not found — corpus stats will be omitted")

    print("\nBuilding report...")
    report = build_report(results, df_critical)

    # Save
    report_path = os.path.join(output_dir, "summary_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nSaved: {report_path}")

    # Console summary
    print(f"\n{'='*60}")
    print("CROSS-PLATFORM SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Platform':<22} {'Themes':>6} {'Student Voice':>14} {'Register'}")
    print(f"  {'-'*22} {'-'*6} {'-'*14} {'-'*30}")
    for r in sorted(results, key=lambda x: x.get("platform", "")):
        sv = "YES ***" if r.get("student_voice", {}).get("present") else "no"
        print(
            f"  {r.get('platform','?'):<22} "
            f"{len(r.get('themes', [])):>6} "
            f"{sv:>14}   "
            f"{r.get('emotional_register', '?')[:35]}"
        )

    print(f"\nDone. Report saved to {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate summary report from per-platform theme JSON files."
    )
    parser.add_argument(
        "--output_dir",
        default="outputs",
        help="Directory containing themes_*.json files (default: outputs/)"
    )
    args = parser.parse_args()
    main(args.output_dir)
