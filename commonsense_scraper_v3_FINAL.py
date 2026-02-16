"""
Common Sense Media Community Review Scraper
NET Lab, Inc. | February 2026
Built with Claude AI (Anthropic)

PURPOSE:
Preserves Common Sense Education community reviews that are publicly accessible
but no longer easily visible on product pages. These peer reviews from teachers,
parents, and students provide valuable firsthand accounts about EdTech tools.

HOW TO USE:
1. Collect review URLs using JavaScript console method (see METHODOLOGY.md)
2. Save URLs in a text file: [product_name]_review_urls.txt (one URL per line)
3. Edit line 31 below: PRODUCT_NAME = "your_product"
4. Run: python commonsense_scraper_v3_FINAL.py
5. Output: commonsense_[product]_YYYYMMDD_HHMMSS.csv

REQUIREMENTS:
- Python 3.x
- Libraries: requests, beautifulsoup4, pandas
- Install: pip install requests beautifulsoup4 pandas

CONTACT:
- Email: meredith@netlab.inc
- Website: netlab.inc
- GitHub: [add your repository URL]

LICENSE: MIT
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import csv
import re

# ============================================================================
# CONFIGURATION - CHANGE THIS FOR EACH PRODUCT
# ============================================================================
PRODUCT_NAME = "kahoot"  # <-- CHANGE THIS (lowercase, no spaces)
# Examples: "iready", "seesaw", "kahoot", "classdojo", "clever"
# ============================================================================

# Don't change these
HEADERS = {
    'User-Agent': 'NET Lab EdTech Research (Academic, meredith@netlab.inc)'
}

INPUT_FILENAME = f'{PRODUCT_NAME}_review_urls.txt'  # File with URLs, one per line
OUTPUT_FILENAME_BASE = f'commonsense_{PRODUCT_NAME}'  # Will add timestamp automatically


def scrape_review(url):
    """
    Scrape a single Common Sense Media review
    
    Args:
        url: URL to the review
        
    Returns:
        Dictionary with review data
    """
    print(f"\nScraping: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Initialize data
        review_data = {
            'url': url,
            'node_id': url.split('/')[-1] if '/node/' in url else '',
            'collected_date': datetime.now().isoformat(),
        }
        
        # Extract review title (the H1)
        h1 = soup.find('h1')
        review_data['review_title'] = h1.get_text(strip=True) if h1 else 'Unknown'
        
        # Extract product name from breadcrumb or link
        # Look for "Community Review for [Product]" or link to product
        product_link = soup.find('a', href=re.compile(r'/education/(reviews|app|website)/'))
        if product_link:
            review_data['product_name'] = product_link.get_text(strip=True)
        else:
            # Try to extract from page title
            page_title = soup.find('title')
            if page_title:
                title_text = page_title.get_text()
                if 'Review of' in title_text:
                    review_data['product_name'] = title_text.split('Review of')[1].split('|')[0].strip()
                else:
                    review_data['product_name'] = 'Unknown'
            else:
                review_data['product_name'] = 'Unknown'
        
        # Note: Reviewer name and role are not reliably extractable from the page structure
        # Removed from output to avoid bad data and streamline CSV cleaning
        
        # Extract date posted
        # Look more specifically for date patterns
        date_text = 'Unknown'
        
        # First try: look for <time> elements (most reliable)
        time_elem = soup.find('time')
        if time_elem:
            # Try datetime attribute first
            if time_elem.has_attr('datetime'):
                date_text = time_elem['datetime']
            else:
                date_text = time_elem.get_text(strip=True)
        else:
            # Second try: look for date patterns in text
            # Patterns like "January 10, 2024" or "3 months ago"
            date_pattern = re.compile(r'(\w+ \d+, \d{4}|Submitted .+ ago|\d+ \w+ ago)')
            
            for elem in soup.find_all(['span', 'p', 'div']):
                text = elem.get_text(strip=True)
                match = date_pattern.search(text)
                if match and len(text) < 100:  # Avoid grabbing entire paragraphs
                    date_text = match.group(1)
                    break
        
        review_data['date_posted'] = date_text
        
        # Note: Ratings (Engagement, Pedagogy, Supports) are not reliably extractable
        # Removed from output to avoid bad data and streamline CSV cleaning
        
        # Extract main review sections
        sections = {}
        
        # Common Sense reviews have sections like "My Take", "How I Use It"
        section_headers = soup.find_all(['h2', 'h3', 'h4'])
        
        for header in section_headers:
            header_text = header.get_text(strip=True)
            
            # STOP if we hit "More community reviews" - that's other people's reviews!
            if 'More community reviews' in header_text:
                break
            
            # Get the content after this header (usually next sibling or parent's next)
            content = ''
            next_elem = header.find_next_sibling()
            
            # Collect text until we hit another header
            while next_elem and next_elem.name not in ['h1', 'h2', 'h3', 'h4']:
                if next_elem.name in ['p', 'div']:
                    # Also stop if we see "More community reviews" in the text
                    text = next_elem.get_text(separator=' ', strip=True)
                    if 'More community reviews' in text:
                        break
                    content += text + '\n'
                next_elem = next_elem.find_next_sibling()
            
            if content.strip():
                sections[header_text] = content.strip()
        
        # Combine all sections into full review text
        if sections:
            full_text = '\n\n'.join([f"### {k}\n{v}" for k, v in sections.items()])
            review_data['review_text'] = full_text
        else:
            # Fallback: get all paragraph text but STOP at "More community reviews"
            paragraphs = []
            for p in soup.find_all('p'):
                p_text = p.get_text(strip=True)
                # Stop if we hit the "More community reviews" section
                if 'More community reviews' in p_text:
                    break
                if len(p_text) > 20:
                    paragraphs.append(p_text)
            review_data['review_text'] = '\n\n'.join(paragraphs)
        
        # Extract specific sections if they exist
        review_data['my_take'] = sections.get('My Take', '')
        review_data['how_i_use_it'] = sections.get('How I Use It', '')
        
        # CLEAN: Remove any "More community reviews" text that slipped through
        for field in ['review_text', 'my_take', 'how_i_use_it']:
            if field in review_data and review_data[field]:
                # Split on "More community reviews" and keep only the first part
                text = review_data[field]
                if 'More community reviews' in text:
                    review_data[field] = text.split('More community reviews')[0].strip()
        
        print(f"  ✓ Extracted review")
        print(f"    Title: {review_data['review_title']}")
        print(f"    Product: {review_data['product_name']}")
        print(f"    Text length: {len(review_data['review_text'])} characters")
        
        # Be respectful - rate limit
        time.sleep(2)
        
        return review_data
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def load_urls_from_file(filename=INPUT_FILENAME):
    """
    Load URLs from text file (one per line)
    
    Args:
        filename: Path to file
        
    Returns:
        List of URLs
    """
    try:
        with open(filename, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
        print(f"✓ Loaded {len(urls)} URLs from {filename}")
        return urls
    except FileNotFoundError:
        return []

def collect_all_reviews(urls):
    """
    Collect all reviews
    
    Args:
        urls: List of review URLs
        
    Returns:
        DataFrame
    """
    all_reviews = []
    
    print(f"\n{'='*60}")
    print(f"Collecting {len(urls)} reviews...")
    print(f"{'='*60}")
    
    for i, url in enumerate(urls, 1):
        print(f"\nReview {i}/{len(urls)}")
        review_data = scrape_review(url)
        if review_data:
            all_reviews.append(review_data)
    
    df = pd.DataFrame(all_reviews)
    
    print(f"\n{'='*60}")
    print(f"Successfully collected {len(df)} reviews")
    print(f"{'='*60}")
    
    return df

def export_to_csv(df, filename=None):
    """Export to CSV for NVivo"""
    if df.empty:
        print("No data to export")
        return
    
    # Generate filename with timestamp if not provided
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{OUTPUT_FILENAME_BASE}_{timestamp}.csv'
    
    df.to_csv(filename, index=False, quoting=csv.QUOTE_ALL)
    
    print(f"\n{'='*60}")
    print(f"EVIDENCE PRESERVED: {PRODUCT_NAME.upper()}")
    print(f"{'='*60}")
    print(f"Data exported to: {filename}")
    print(f"Total reviews: {len(df)}")
    
    print(f"\nProducts reviewed:")
    if 'product_name' in df.columns:
        print(df['product_name'].value_counts().to_string())
    
    if 'date_posted' in df.columns:
        print(f"\nDate extraction:")
        dates_found = df['date_posted'].value_counts()
        unknown_count = dates_found.get('Unknown', 0)
        known_count = len(df) - unknown_count
        print(f"  Found dates: {known_count}/{len(df)}")
        if unknown_count > 0:
            print(f"  Unknown dates: {unknown_count}")
    
    print(f"\n{'='*60}")
    print(f"These reviews document community feedback that Common Sense Media")
    print(f"no longer displays prominently on {PRODUCT_NAME}'s product page.")
    print("CSV ready for analysis in Excel, NVivo, or other tools.")
    print(f"{'='*60}")

def main():
    """Main execution"""
    print("="*60)
    print("Common Sense Media Review Scraper")
    print(f"NET Lab - Documenting {PRODUCT_NAME.upper()} Reviews")
    print("="*60)
    
    # Try to load from file
    urls = load_urls_from_file()
    
    if not urls:
        print("\n⚠ No URLs found!")
        print(f"\nCreate a file named: {INPUT_FILENAME}")
        print("Add one URL per line.")
        print("\nSee METHODOLOGY.md for URL collection instructions.")
        return
    
    # Collect reviews
    df = collect_all_reviews(urls)
    
    # Export
    if not df.empty:
        export_to_csv(df)
    else:
        print("\n⚠ No reviews collected. Check URLs and try again.")

if __name__ == "__main__":
    main()
