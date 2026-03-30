# Common Sense Education Community Review Archive
## Methodology Documentation

**Project:** NET Lab EdTech Review Preservation  
**Researcher:** Meredith Bouvier, PhD (NET Lab, Inc.)  
**Date:** March 2026  
**Contact:** merrybouv@proton.me  

---

## Overview

This archive systematically preserves Common Sense Education community reviews for widely-used K-12 educational technology products. These reviews from teachers, parents, and students represent over a decade of firsthand accounts that are no longer publicly accessible on Common Sense Education product pages.

### Background: Why This Archive Exists

Using the Internet Archive Wayback Machine, I confirmed that community reviews were publicly accessible on Common Sense Education product pages as recently as early 2025. By January 2026, dedicated review sections had been removed. By March 2026, individual review URLs were also inaccessible.

This archive preserves what was collected in February 2026 (February 3–16) before the archive closed entirely.

---

## Data Collection Process

Note: Individual review URLs became inaccessible in March 2026. The collection process documented here cannot be replicated; this methodology is preserved as part of the scholarly record of how the corpus was created.

### Stage 1: URL Collection (Manual)

**Search Method:**
- Platform: Google Search
- Query format: `site:commonsense.org/node "community review of [product]"`
- Filter setting: "Repeat the search with the omitted results included"

**URL Extraction:**
- Tool: Browser Developer Console (JavaScript)
- Method: Console script (`console_script.js`) extracts all Common Sense review URLs from search results

**URL Filtering:**
For products frequently mentioned in reviews of other tools, URLs were manually filtered to include only reviews where the target product was the primary subject.

**Output:**
- Text file per product: `[product]_review_urls.txt`
- One URL per line

### Stage 2: Review Content Scraping (Automated)

**Tool:** Python scraper (`commonsense_scraper_v3_FINAL.py`)

**Process:**
1. Reads URL list for target product
2. Fetches each review page (2-second delay between requests)
3. Extracts structured data from HTML
4. Exports to CSV with timestamp

**Data Fields Extracted:**
- `url` — Original review URL
- `node_id` — Common Sense internal identifier
- `collected_date` — Timestamp of scraping
- `product_name` — Name of product reviewed
- `date_posted` — When review was submitted (format varies)
- `review_text` — Full review content
- `my_take` — "My Take" section
- `how_i_use_it` — "How I Use It" section

**Fields not retained:**
- `reviewer_name` — Blank in most cases, removed after collection
- `ratings` — Extraction unreliable, removed after collection
- `review_title` — Extraction unsuccessful, removed after collection

**Output:**
- CSV file per product: `commonsense_[product]_YYYYMMDD_HHMMSS.csv`

### Stage 3: Data Cleaning (Manual)

- CSV files reviewed in spreadsheet software
- Rows removed where `product_name` does not match target product
- Cleaned CSVs uploaded to OSF

---

## Analysis Pipeline

A three-step analysis pipeline was developed after collection:

- `01_score_reviews.py` — applies 77-term concern vocabulary index
- `02_analyze_themes.py` — thematic analysis via Claude API
- `03_summary_report.py` — generates cross-platform markdown report
- `generate_wordcloud.py` — word cloud from full corpus

See README.md for usage instructions.

---

## Technical Specifications

- Language: Python 3.x
- Key libraries: requests, BeautifulSoup4, pandas, anthropic, wordcloud
- Rate limiting: 2-second delay between requests
- Data storage: OSF (public), ProtonDrive (private backup)

---

## Data Quality and Limitations

**Limitations:**
- Collection bounded by Google search index — not a complete census of all reviews ever posted
- Reviews span approximately 2014 to early 2025; dates stored as relative strings
- Reviewer names not retained; most were anonymous
- Rating values not reliably extractable

**Strengths:**
- Systematic collection with no selective sampling by content or sentiment
- All available reviews captured for seven platforms
- URLs preserved for verification
- Fully documented and reproducible methodology

---

## Products Included

619 reviews across 7 platforms collected February 3–16, 2026:

1. ClassDojo (128 reviews)
2. Google Classroom (20 reviews)
3. iReady (50 reviews)
4. IXL (99 reviews)
5. Kahoot (227 reviews)
6. Quizlet (50 reviews)
7. Seesaw (45 reviews)

Collection is complete. No further products will be added.

---

## Ethical Considerations

- All reviews were publicly accessible at time of collection
- No authentication required
- Original URLs preserved in dataset
- Rate limiting implemented throughout
- No commercial use

---

## Citation
```
Bouvier, M. (2026). Common Sense Education Community Review Archive. 
Open Science Framework. https://osf.io/ehbfv/
Code: https://github.com/merrybouv/common-sense-review-archive
```

---

## Contact

Meredith Bouvier, PhD  
NET Lab, Inc. (Delaware Public Benefit Corporation)  
merrybouv@proton.me  
https://orcid.org/0009-0009-0978-5231

---

## License

- Code: MIT License  
- Data: CC BY 4.0