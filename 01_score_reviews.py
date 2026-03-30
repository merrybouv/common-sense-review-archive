"""
01_score_reviews.py
===================
Common Sense Education Review Archive — Step 1 of 3
Meredith Bouvier, PhD | NET Lab, Inc.

PURPOSE
-------
Loads all scraped Common Sense Education review CSVs, applies a
documented concern-vocabulary scoring index, and outputs two files:

    outputs/all_reviews_scored.csv   — full corpus with scores appended
    outputs/critical_reviews.csv     — subset scoring >= THRESHOLD

VOCABULARY INDEX
----------------
Scoring is based on substring matching against a curated list of
concern terms grouped into seven thematic categories:

    1. stress_anxiety        emotional distress language
    2. compulsion            addictive / compulsive use language
    3. privacy_data          surveillance / data collection concerns
    4. pedagogy              rote / shallow / non-learning critique
    5. access_equity         cost / paywall / equity barriers
    6. direct_negative       explicit rejection language
    7. behavior_surveillance public shaming / behavior modification critique

Each review receives a raw integer score (number of matched terms).
The threshold for "critical" is set at THRESHOLD = 2 (configurable).

A review scoring >= 2 matched terms is treated as expressing substantive
concern. Matched terms are saved alongside the score for transparency.

This is an intentionally conservative, lexical approach — not sentiment
analysis. It is designed to be fully reproducible without ML dependencies.

INPUTS
------
    data/                           directory of scraped CSVs
        commonsense_[product]_*.csv

OUTPUTS
-------
    outputs/all_reviews_scored.csv  all 619 reviews with score columns
    outputs/critical_reviews.csv    reviews scoring >= THRESHOLD

USAGE
-----
    # from repo root with netlab_env activated:
    python 01_score_reviews.py

    # custom data directory or threshold:
    python 01_score_reviews.py --data_dir /path/to/csvs --threshold 3

DEPENDENCIES
------------
    pandas
    (no API calls, no internet required)

CITATION
--------
    Bouvier, M. (2026). Common Sense Education Community Review Archive.
    Open Science Framework. https://osf.io/ehbfv/
    Code: https://github.com/merrybouv/common-sense-review-archive
"""

import os
import glob
import argparse
import pandas as pd


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

THRESHOLD = 2  # minimum concern score to be included in critical_reviews.csv

# Concern vocabulary index — grouped by theme for transparency
# Each entry is a substring (case-insensitive match against full review text)
CONCERN_VOCABULARY = {
    "stress_anxiety": [
        "stress", "stressed", "anxious", "anxiety", "overwhelm",
        "frustrat", "upset", "cry", "cried", "tears", "meltdown", "panic",
    ],
    "compulsion": [
        "addict", "obsess", "compulsive", "can't stop", "glued",
        "screen time", "too much time", "excessive",
    ],
    "privacy_data": [
        "privacy", "tracking", "surveillance", "personal information",
        "gdpr", "coppa", "selling data", "data mining", "data collect",
    ],
    "pedagogy": [
        "drill", "rote", "mindless", "shallow", "superficial",
        "no learning", "doesn't learn", "not learning", "replace teacher",
    ],
    "access_equity": [
        "paywall", "subscription", "expensive", "can't afford", "equity",
        "low income",
    ],
    "direct_negative": [
        "hate", "terrible", "awful", "horrible", "worst", "dangerous",
        "harmful", "inappropriate", "refuse", "concern", "worried", "worry",
        "problem", "complaint", "dislike", "disappoint", "mislead",
        "manipulat", "no no", "stop using", "do not use",
        "do not recommend", "not recommend", "push back", "opt out",
        "deleted",
    ],
    "behavior_surveillance": [
        "shame", "embarrass", "humiliat", "punish", "negative point",
        "behavior modif", "public discipline",
    ],
}

# Flat list for scoring (duplicates across categories are fine — we deduplicate on match)
ALL_TERMS = list({term for terms in CONCERN_VOCABULARY.values() for term in terms})


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def score_review(text: str) -> tuple[int, list[str]]:
    """
    Score a review text against the concern vocabulary index.

    Parameters
    ----------
    text : str
        Combined review text (my_take + review_text fields).

    Returns
    -------
    score : int
        Number of distinct concern terms matched.
    matched : list[str]
        The specific terms that matched, for transparency.
    """
    if not isinstance(text, str) or not text.strip():
        return 0, []
    text_lower = text.lower()
    matched = [term for term in ALL_TERMS if term in text_lower]
    return len(matched), matched


def load_csvs(data_dir: str) -> pd.DataFrame:
    """
    Load all commonsense_*.csv files from data_dir into a single DataFrame.
    Infers platform name from filename if not present in data.

    Parameters
    ----------
    data_dir : str
        Path to directory containing scraped CSVs.

    Returns
    -------
    pd.DataFrame
        Combined corpus with a 'platform' column added.
    """
    pattern = os.path.join(data_dir, "commonsense_*.csv")
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(
            f"No commonsense_*.csv files found in '{data_dir}'.\n"
            f"Expected files like: commonsense_classdojo_20260203_150345.csv"
        )

    dfs = []
    for filepath in files:
        df = pd.read_csv(filepath)

        # Infer platform from filename if column not present
        if "platform" not in df.columns:
            basename = os.path.basename(filepath)          # commonsense_classdojo_20260203.csv
            parts = basename.replace("commonsense_", "").split("_")
            platform_raw = parts[0] if parts else "unknown"
            platform_display = {
                "classdojo": "ClassDojo",
                "google": "Google Classroom",
                "iready": "iReady",
                "ixl": "IXL",
                "kahoot": "Kahoot",
                "quizlet": "Quizlet",
                "seesaw": "Seesaw",
            }.get(platform_raw.lower(), platform_raw.title())
            df["platform"] = platform_display

        dfs.append(df)
        print(f"  Loaded: {os.path.basename(filepath)} ({len(df)} reviews)")

    combined = pd.concat(dfs, ignore_index=True)
    return combined


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(data_dir: str, threshold: int, output_dir: str):

    print(f"\n{'='*60}")
    print("01_score_reviews.py — Common Sense Education Review Archive")
    print(f"{'='*60}")
    print(f"Data directory : {data_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Concern threshold: score >= {threshold}")
    print(f"Vocabulary terms : {len(ALL_TERMS)} terms across {len(CONCERN_VOCABULARY)} categories")
    print()

    # Load
    print("Loading CSVs...")
    df = load_csvs(data_dir)
    print(f"\nTotal reviews loaded: {len(df)}")

    # Build combined text field for scoring
    df["combined_text"] = (
        df.get("my_take", pd.Series("", index=df.index)).fillna("") + " " +
        df.get("review_text", pd.Series("", index=df.index)).fillna("")
    ).str.strip()

    # Score
    print("\nScoring reviews...")
    results = df["combined_text"].apply(lambda t: pd.Series(score_review(t), index=["concern_score", "matched_terms"]))
    df["concern_score"] = results["concern_score"]
    df["matched_terms"] = results["matched_terms"].apply(lambda x: "|".join(x))  # CSV-safe

    # Per-platform summary
    print("\nConcern score distribution by platform:")
    print(f"  {'Platform':<22} {'Total':>6} {'Score 0':>8} {'Score 1':>8} {'Score 2':>8} {'Score 3+':>9} {'Mean':>6}")
    print(f"  {'-'*22} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*9} {'-'*6}")
    for platform, grp in df.groupby("platform"):
        s = grp["concern_score"]
        print(
            f"  {platform:<22} {len(grp):>6} {sum(s==0):>8} {sum(s==1):>8} "
            f"{sum(s==2):>8} {sum(s>=3):>9} {s.mean():>6.2f}"
        )

    total_critical = sum(df["concern_score"] >= threshold)
    print(f"\nTotal reviews with score >= {threshold}: {total_critical} of {len(df)} ({100*total_critical/len(df):.1f}%)")

    # Save outputs
    os.makedirs(output_dir, exist_ok=True)

    all_path = os.path.join(output_dir, "all_reviews_scored.csv")
    df.drop(columns=["combined_text"]).to_csv(all_path, index=False)
    print(f"\nSaved: {all_path}")

    critical = df[df["concern_score"] >= threshold].copy()
    critical_path = os.path.join(output_dir, "critical_reviews.csv")
    critical.drop(columns=["combined_text"]).to_csv(critical_path, index=False)
    print(f"Saved: {critical_path} ({len(critical)} reviews)")

    # Vocabulary category breakdown (for methods section)
    print("\nVocabulary categories and term counts:")
    for category, terms in CONCERN_VOCABULARY.items():
        print(f"  {category:<25} {len(terms):>3} terms")

    print(f"\nDone. Run 02_analyze_themes.py next.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Score Common Sense Education reviews by concern vocabulary."
    )
    parser.add_argument(
        "--data_dir",
        default="data",
        help="Directory containing commonsense_*.csv files (default: data/)"
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=THRESHOLD,
        help=f"Minimum score for critical_reviews.csv (default: {THRESHOLD})"
    )
    parser.add_argument(
        "--output_dir",
        default="outputs",
        help="Directory for output CSVs (default: outputs/)"
    )
    args = parser.parse_args()
    main(args.data_dir, args.threshold, args.output_dir)
