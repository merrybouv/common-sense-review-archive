"""
Product Review Counter
NET Lab, Inc. | February 2026

Searches Google to estimate how many reviews exist for each EdTech product
on Common Sense Media. Helps prioritize which products to scrape first.

HOW TO USE:
1. Edit the PRODUCTS list below (add your top 20 products)
2. Run: python product_review_counter.py
3. Output: product_review_counts.csv (sorted by estimated review count)

Takes ~5 minutes to run (to respect Google rate limits)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

# ============================================================================
# EDIT THIS LIST - Your Products to Check
# ============================================================================
PRODUCTS = [
    # Learning Management Systems
    "Google Classroom",
    "Canvas",
    "Schoology",
    "Seesaw",
    "ClassDojo",
    "Edmodo",
    "Blackboard",
    
    # Assessment & Adaptive Learning
    "iReady",
    "Kahoot",
    "Quizlet",
    "Quizizz",
    "Nearpod",
    "Pear Deck",
    "IXL",
    "Edpuzzle",
    "Socrative",
    "Formative",
    
    # Reading & Literacy
    "Epic",
    "Raz-Kids",
    "Reading Eggs",
    "Lexia",
    "Starfall",
    "ABCmouse",
    "Newsela",
    
    # Math & STEM
    "Khan Academy",
    "Prodigy",
    "DreamBox",
    "Zearn",
    "Desmos",
    "GeoGebra",
    "STMath",
    
    # Communication & Collaboration
    "Remind",
    "ClassTag",
    "Bloomz",
    "Flipgrid",
    "Flip",
    "Padlet",
    "Jamboard",
    
    # Single Sign-On & Access
    "Clever",
    "ClassLink",
    
    # Video & Creation Tools
    "Screencastify",
    "WeVideo",
    "Book Creator",
    "Canva for Education",
    
    # Behavior & SEL
    "Second Step",
    "Calm Classroom",
    
    # Language Learning
    "Duolingo",
    "Rosetta Stone",
    "Babbel",
    
    # Other Popular Tools
    "BrainPOP",
]
# ============================================================================

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_review_count(product_name):
    """
    Search Google and extract estimated result count
    
    Args:
        product_name: Name of the product
        
    Returns:
        Tuple of (product_name, estimated_count)
    """
    # Build search query
    query = f'site:commonsense.org/node {product_name}'
    search_url = f'https://www.google.com/search?q={query}'
    
    print(f"Checking: {product_name}...", end=" ")
    
    try:
        response = requests.get(search_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for "About X results" text
        # Google shows this in a div with id="result-stats"
        result_stats = soup.find('div', id='result-stats')
        
        if result_stats:
            stats_text = result_stats.get_text()
            # Extract number from "About 150 results" or "150 results"
            match = re.search(r'About\s+([\d,]+)\s+results?|^([\d,]+)\s+results?', stats_text)
            
            if match:
                count_str = match.group(1) or match.group(2)
                count = int(count_str.replace(',', ''))
                print(f"✓ ~{count} reviews")
                return (product_name, count)
        
        # Fallback: count actual search result links
        # (Less accurate but better than nothing)
        links = soup.find_all('a', href=re.compile(r'commonsense\.org/node/\d+'))
        fallback_count = len(links)
        print(f"⚠ ~{fallback_count}+ reviews (estimated from page 1 only)")
        return (product_name, fallback_count)
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return (product_name, 0)

def main():
    """Main execution"""
    print("="*60)
    print("Product Review Counter")
    print("NET Lab - Estimating Review Counts for EdTech Products")
    print("="*60)
    print(f"\nChecking {len(PRODUCTS)} products...")
    print("This takes ~5 minutes (rate limiting for Google)\n")
    
    results = []
    
    for i, product in enumerate(PRODUCTS, 1):
        print(f"[{i}/{len(PRODUCTS)}] ", end="")
        product_name, count = get_review_count(product)
        results.append({
            'product': product_name,
            'estimated_reviews': count
        })
        
        # Rate limiting - be respectful to Google
        if i < len(PRODUCTS):
            print("    Waiting 15 seconds...")
            time.sleep(15)
    
    # Create DataFrame and sort by count
    df = pd.DataFrame(results)
    df = df.sort_values('estimated_reviews', ascending=False)
    
    # Save to CSV
    output_file = 'product_review_counts.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    print(df.to_string(index=False))
    print(f"\n{'='*60}")
    print(f"Saved to: {output_file}")
    print(f"\nTop 5 products with most reviews:")
    for idx, row in df.head(5).iterrows():
        print(f"  {idx+1}. {row['product']}: ~{row['estimated_reviews']} reviews")
    print(f"{'='*60}")
    print("\nRecommendation: Start with the top products!")
    print("They'll give you the richest datasets.")

if __name__ == "__main__":
    main()
