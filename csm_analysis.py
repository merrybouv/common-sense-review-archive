"""
Common Sense Media Review Corpus — Analysis Pipeline
NET Lab, Inc. | March 2026
Meredith Bouvier, PhD

SETUP (run once):
    source ~/netlab_env/bin/activate
    pip install bertopic sentence-transformers scikit-learn pandas matplotlib umap-learn

USAGE:
    python csm_analysis.py

OUTPUTS (all saved to OUTPUT_DIR):
    corpus_combined.csv         — all reviews merged
    top_words.csv               — most common words with counts and % of reviews
    top_words.png               — bar chart of top 40 words
    bertopic_topics.csv         — topic labels and top words per topic
    bertopic_assignments.csv    — each review assigned to a topic
    bertopic_visualization.html — interactive topic browser (open in browser)
    term_frequency.csv          — your custom term list with counts and % of reviews
    term_frequency.png          — comparison chart

WORKFLOW:
    Step 1 — Run the script
    Step 2 — Look at top_words.csv and bertopic_topics.csv
    Step 3 — Edit CUSTOM_TERMS below based on what you see
    Step 4 — Re-run to get updated term_frequency results
"""

import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import Counter
from umap import UMAP

# ============================================================
# CONFIGURATION
# ============================================================

CSV_FILES = {
    'ClassDojo':        '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_classdojo_20260203_150345.csv',
    'Seesaw':           '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_seesaw_20260206_082959.csv',
    'Google Classroom': '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_google_classroom_20260216_101512.csv',
    'iReady':           '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_iready_20260204_131252.csv',
    'IXL':              '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_ixl_20260210_195402.csv',
    'Kahoot':           '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_kahoot_20260206_085955.csv',
    'Quizlet':          '/Volumes/External/NET_Lab/Common_Sense_Media/commonsense_quizlet_20260216_103351.csv',
}

OUTPUT_DIR = '/Volumes/External/NET_Lab/Common_Sense_Media/csm_analysis_outputs'

# ============================================================
# CUSTOM TERMS — edit after reviewing top_words and BERTopic
# ============================================================

CUSTOM_TERMS = {
    'optimization': [
        'learning', 'skills', 'engagement', 'effectiveness',
        'outcomes', 'achievement', 'performance', 'motivation', 'progress',
        'assessment', 'practice', 'mastery', 'proficiency',
    ],
    'governance': [
        'privacy', 'data', 'tracking', 'advertising', 'data collection',
        'surveillance', 'consent', 'data rights', 'third party',
        'commercial', 'monetization', 'exploitation',
    ],
    'concern': [
        'problem', 'issue', 'frustrat', 'concern', 'stress', 'anxiety',
        'distract', 'addictive', 'screen time', 'harmful', 'inappropriate',
        'negative', 'wrong', 'competition', 'competitive', 'reward',
        'points', 'earn', 'behavior', 'punishment', 'screen',
    ],
}

# ============================================================
# STOPWORDS
# ============================================================

STOPWORDS = {
    'i','the','a','an','and','to','of','it','is','in','my','for','that',
    'this','with','are','have','they','be','as','on','not','we','use',
    'can','has','at','or','but','was','all','so','do','by','if','more',
    'from','up','their','our','its','also','very','would','which','about',
    'one','when','get','your','you','been','what','there','some','how',
    'used','using','who','had','no','will','just','out','into','other',
    'each','me','them','time','were','than','then','like','any','well',
    'class','students','student','teachers','teacher','tool','tools',
    'app','apps','school','classroom','kahoot','classdojo','seesaw',
    'ixl','iready','quizlet','google','platform','program','website',
    'online','digital','work','really','great','love','good','easy',
    'make','made','way','even','much','many','new','only','does','need',
    'able','find','think','know','see','give','take','want','set','go',
    'got','come','own','little','while','where','most','both','after',
    'should','could','these','those','through','because','now','here',
    'sure','something','things','thing','lot','feel','always','never',
    'every','still','different','between','over','back','being','however',
    'feature','features','overall','nice','wonderful','awesome','amazing',
    'best','better','useful','s','t','don','ve','re','ll','d','m',
}

# ============================================================
# STEP 1 — Load and combine all CSVs
# ============================================================

def load_corpus(csv_files):
    print("\n" + "="*60)
    print("STEP 1: Loading corpus")
    print("="*60)
    dfs = []
    for platform, path in csv_files.items():
        if not os.path.exists(path):
            print(f"  WARNING: {path} not found — skipping {platform}")
            continue
        df = pd.read_csv(path)
        df['platform'] = platform
        print(f"  {platform}: {len(df)} reviews")
        dfs.append(df)
    corpus = pd.concat(dfs, ignore_index=True)
    corpus['full_text'] = (
        corpus['review_text'].fillna('') + ' ' +
        corpus['my_take'].fillna('') + ' ' +
        corpus['how_i_use_it'].fillna('')
    ).str.strip()
    corpus = corpus[corpus['full_text'].str.len() > 50].reset_index(drop=True)
    print(f"\n  Total: {len(corpus)} reviews across {corpus['platform'].nunique()} platforms")
    return corpus

# ============================================================
# STEP 2 — Most common words
# ============================================================

def top_words(corpus, n=150):
    print("\n" + "="*60)
    print("STEP 2: Top words analysis")
    print("="*60)
    all_words = []
    for text in corpus['full_text']:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        all_words.extend([w for w in words if w not in STOPWORDS])
    counter = Counter(all_words)
    rows = []
    total = len(corpus)
    for word, count in counter.most_common(n):
        pct = sum(1 for t in corpus['full_text'].str.lower() if word in t) / total * 100
        rows.append({'word': word, 'count': count, 'pct_reviews': round(pct, 1)})
    df_words = pd.DataFrame(rows)
    out = os.path.join(OUTPUT_DIR, 'top_words.csv')
    df_words.to_csv(out, index=False)
    print(f"  Saved: {out}")
    print(f"\n  Top 30 words:")
    for _, row in df_words.head(30).iterrows():
        bar = '█' * int(row['pct_reviews'] / 2)
        print(f"    {row['word']:<20} {row['pct_reviews']:>5.1f}%  {bar}")
    top40 = df_words.head(40)
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.barh(top40['word'][::-1], top40['pct_reviews'][::-1], color='#1D9E75')
    ax.set_xlabel('% of reviews containing word')
    ax.set_title('Top 40 words in CSM practitioner reviews (619 reviews, 7 platforms)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    chart_out = os.path.join(OUTPUT_DIR, 'top_words.png')
    plt.savefig(chart_out, dpi=150)
    plt.close()
    print(f"  Chart saved: {chart_out}")
    return df_words

# ============================================================
# STEP 3 — BERTopic
# ============================================================

def run_bertopic(corpus):
    print("\n" + "="*60)
    print("STEP 3: BERTopic topic modeling")
    print("="*60)
    try:
        from bertopic import BERTopic
        from sklearn.feature_extraction.text import CountVectorizer
        print("  BERTopic loaded.")
    except ImportError:
        print("  BERTopic not installed. Run:")
        print("  pip install bertopic sentence-transformers umap-learn")
        print("  Skipping topic modeling.")
        return None

    docs = corpus['full_text'].tolist()
    vectorizer = CountVectorizer(stop_words='english', min_df=2)
    umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42)
    model = BERTopic(
        vectorizer_model=vectorizer,
        umap_model=umap_model,
        min_topic_size=20,
        calculate_probabilities=False,
        verbose=True,
    )
    topics, _ = model.fit_transform(docs)
    corpus['topic'] = topics

    topic_info = model.get_topic_info()
    print(f"\n  {len(topic_info) - 1} topics found (plus noise topic -1)")
    print(f"\n  Topic summary:")
    for _, row in topic_info.iterrows():
        if row['Topic'] == -1:
            print(f"    Topic -1 (noise): {row['Count']} reviews")
        else:
            words = [w for w, _ in model.get_topic(row['Topic'])[:8]]
            print(f"    Topic {row['Topic']} ({row['Count']} reviews): {', '.join(words)}")

    topic_out = os.path.join(OUTPUT_DIR, 'bertopic_topics.csv')
    topic_info.to_csv(topic_out, index=False)
    print(f"\n  Topics saved: {topic_out}")

    assign_out = os.path.join(OUTPUT_DIR, 'bertopic_assignments.csv')
    corpus[['url', 'platform', 'topic', 'full_text']].to_csv(assign_out, index=False)
    print(f"  Assignments saved: {assign_out}")

    try:
        fig = model.visualize_topics()
        viz_out = os.path.join(OUTPUT_DIR, 'bertopic_visualization.html')
        fig.write_html(viz_out)
        print(f"  Interactive viz saved: {viz_out}")
    except Exception as e:
        print(f"  Visualization skipped: {e}")

    return model

# ============================================================
# STEP 4 — Custom term frequency
# ============================================================

def term_frequency(corpus, terms):
    print("\n" + "="*60)
    print("STEP 4: Custom term frequency")
    print("="*60)
    texts = corpus['full_text'].str.lower().tolist()
    n = len(texts)
    rows = []
    for category, term_list in terms.items():
        for term in term_list:
            count = sum(1 for t in texts if term in t)
            rows.append({
                'category': category,
                'term': term,
                'count': count,
                'pct_reviews': round(100 * count / n, 1),
            })
    df_terms = pd.DataFrame(rows).sort_values(['category', 'pct_reviews'], ascending=[True, False])
    out = os.path.join(OUTPUT_DIR, 'term_frequency.csv')
    df_terms.to_csv(out, index=False)
    print(f"  Saved: {out}")
    for cat in df_terms['category'].unique():
        print(f"\n  --- {cat.upper()} ---")
        sub = df_terms[df_terms['category'] == cat]
        for _, row in sub.iterrows():
            bar = '█' * int(row['pct_reviews'] / 2)
            print(f"    {row['term']:<25} {row['pct_reviews']:>5.1f}%  {bar}")
    colors = {'optimization': '#1D9E75', 'governance': '#D85A30', 'concern': '#7F77DD'}
    fig, axes = plt.subplots(1, 3, figsize=(15, 7))
    for ax, (cat, color) in zip(axes, colors.items()):
        sub = df_terms[df_terms['category'] == cat].sort_values('pct_reviews')
        ax.barh(sub['term'], sub['pct_reviews'], color=color)
        ax.set_title(cat.capitalize())
        ax.set_xlabel('% of reviews')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    plt.suptitle('Term frequency in CSM practitioner reviews (619 reviews, 7 platforms)', y=1.02)
    plt.tight_layout()
    chart_out = os.path.join(OUTPUT_DIR, 'term_frequency.png')
    plt.savefig(chart_out, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"\n  Chart saved: {chart_out}")
    return df_terms

# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    corpus = load_corpus(CSV_FILES)
    corpus.to_csv(os.path.join(OUTPUT_DIR, 'corpus_combined.csv'), index=False)

    top_words(corpus)
    run_bertopic(corpus)
    term_frequency(corpus, CUSTOM_TERMS)

    print("\n" + "="*60)
    print(f"Done. All outputs in: {OUTPUT_DIR}/")
    print("="*60)
