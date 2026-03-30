"""
generate_wordcloud.py
=====================
Common Sense Education Review Archive — Supplementary Script
Meredith Bouvier, PhD | NET Lab, Inc.

PURPOSE
-------
Generates a word cloud from the full 619-review corpus to illustrate
the nature of the community knowledge infrastructure that was removed
from public access. The predominantly positive valence establishes that
this was a functioning practitioner forum — not a complaint repository.

Within this corpus, 10.8% of reviews expressed substantive concern using
practitioner language. Any forum where critical voice can accumulate and
persist as a searchable public record represents a liability for vendors,
regardless of the proportion that is critical. The figure contextualizes
what was lost: not a collection of grievances, but a decade of community
knowledge that included a meaningful minority of concern-based accounts.

INPUTS
------
    outputs/all_reviews_scored.csv      full scored corpus from step 01

OUTPUTS
-------
    outputs/wordcloud_full_corpus.png   word cloud figure (300 DPI)

USAGE
-----
    # from analysis_pipeline directory with netlab_env activated:
    python generate_wordcloud.py

    # custom colors or output path:
    python generate_wordcloud.py --output outputs/wordcloud_full_corpus.png

DEPENDENCIES
------------
    pandas, wordcloud, matplotlib

    pip install wordcloud matplotlib

NOTE
----
    This script is supplementary — it is not part of the main 3-step
    pipeline and does not need to be run to produce the summary report.

CITATION
--------
    Bouvier, M. (2026). Common Sense Education Community Review Archive.
    Open Science Framework. https://osf.io/ehbfv/
    Code: https://github.com/merrybouv/common-sense-review-archive
"""

import os
import argparse
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Standard English stopwords plus domain-specific terms that add no meaning
CUSTOM_STOPWORDS = STOPWORDS | {
    # Generic
    "use", "used", "using", "uses", "also", "one", "get", "got", "well",
    "will", "can", "would", "could", "make", "made", "like", "just",
    "really", "even", "much", "many", "way", "ways", "time", "times",
    "good", "great", "very", "need", "needs", "still", "thing", "things",
    "want", "wanted", "work", "works", "working", "find", "found",
    "give", "given", "gives", "go", "going", "help", "helps", "helpful",
    "know", "lot", "nan", "new", "now", "able", "back", "come", "day",
    "first", "every", "little", "look", "may", "never", "people",
    "see", "take", "think", "though", "without", "yes", "level", "set", "low", "pre", "etc",
    # Platform names (not analytically useful in full corpus cloud)
    "classdojo", "dojo", "class", "iready", "ready", "ixl", "kahoot",
    "quizlet", "seesaw", "google", "classroom",
    # Review boilerplate
    "review", "product", "tool", "app", "site", "website", "program",
    "platform", "resource", "overall", "opinion", "experience",
}

# Visual configuration
FIGURE_WIDTH_INCHES = 10
FIGURE_HEIGHT_INCHES = 6
DPI = 300
BACKGROUND_COLOR = "white"
COLORMAP = "Blues"         # professional, publication-appropriate
MAX_WORDS = 150
MIN_FONT_SIZE = 10


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main(input_file: str, output_path: str):

    print(f"\n{'='*60}")
    print("generate_wordcloud.py — Common Sense Education Review Archive")
    print(f"{'='*60}")
    print(f"Input : {input_file}")
    print(f"Output: {output_path}")

    # Load corpus
    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"Input file not found: {input_file}\n"
            "Run 01_score_reviews.py first."
        )

    df = pd.read_csv(input_file)
    total_reviews = len(df)
    critical_reviews = sum(df["concern_score"] >= 2)
    print(f"\nLoaded {total_reviews} reviews")
    print(f"Critical reviews (score >= 2): {critical_reviews} ({100*critical_reviews/total_reviews:.1f}%)")

    # Combine all review text
    text_fields = ["my_take", "how_i_use_it", "review_text"]
    combined_text = ""
    for field in text_fields:
        if field in df.columns:
            combined_text += " " + df[field].fillna("").str.cat(sep=" ")
    combined_text = combined_text.strip()

    if not combined_text:
        raise ValueError("No text found in review columns.")

    print(f"Combined text length: {len(combined_text):,} characters")

    # Generate word cloud
    print("\nGenerating word cloud...")
    wc = WordCloud(
        width=FIGURE_WIDTH_INCHES * DPI,
        height=FIGURE_HEIGHT_INCHES * DPI,
        background_color=BACKGROUND_COLOR,
        colormap=COLORMAP,
        stopwords=CUSTOM_STOPWORDS,
        max_words=MAX_WORDS,
        min_font_size=MIN_FONT_SIZE,
        collocations=False,   # avoid repeating bigrams
        prefer_horizontal=0.85,
    ).generate(combined_text)

    # Plot
    fig, ax = plt.subplots(figsize=(FIGURE_WIDTH_INCHES, FIGURE_HEIGHT_INCHES))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")

    # Caption as figure subtitle
    fig.text(
        0.5, 0.02,
        f"Figure: Word cloud of full corpus ({total_reviews} reviews, 7 platforms). "
        f"The predominantly positive valence illustrates a functioning community knowledge "
        f"infrastructure — not a complaint forum. Within this corpus, {critical_reviews} "
        f"reviews ({100*critical_reviews/total_reviews:.1f}%) expressed substantive concern "
        f"using practitioner language now absent from public access.",
        ha="center",
        fontsize=8,
        color="#444444",
        style="italic",
        wrap=True
    )

    plt.tight_layout(rect=[0, 0.06, 1, 1])

    # Save
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    plt.savefig(output_path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close()

    print(f"Saved: {output_path}")
    print(f"\nDone.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate word cloud from full CSM review corpus."
    )
    parser.add_argument(
        "--input",
        default="outputs/all_reviews_scored.csv",
        help="Path to all_reviews_scored.csv from step 01 (default: outputs/all_reviews_scored.csv)"
    )
    parser.add_argument(
        "--output",
        default="outputs/wordcloud_full_corpus.png",
        help="Output path for PNG figure (default: outputs/wordcloud_full_corpus.png)"
    )
    args = parser.parse_args()
    main(args.input, args.output)
