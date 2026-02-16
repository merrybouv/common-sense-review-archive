# Common Sense Education Community Review Archive

Systematic preservation of Common Sense Education community reviews for widely-used EdTech products. These peer reviews from teachers, parents, and students represent over a decade of firsthand accounts but are no longer easily accessible on Common Sense Media product pages.

**Maintained by:** [NET Lab, Inc.](https://netlabconsulting.net) | Meredith Bouvier, PhD

**Dataset:** Available on [Open Science Framework (OSF)](https://osf.io/ehbfv/)

**Built with:** [Claude AI](https://claude.ai) (Anthropic)

---

## 📊 The Data

**Complete dataset:** https://osf.io/ehbfv/

All scraped review CSVs are hosted on OSF for download. This repository contains the code and methodology used to collect the data.

### Products Archived (as of February 16 2026)
See the complete dataset with all products at: https://osf.io/ehbfv/

Archive includes widely-used EdTech products across categories:
- Learning Management Systems (Google Classroom, Canvas, Schoology, etc.)
- Assessment Tools (Kahoot, Quizlet, IXL, etc.)
- Behavior & Communication (ClassDojo, Seesaw, etc.)
- Reading & Math Platforms
- And more...

_Actively expanding - approximately 3 products added per week._

## 🎯 Why This Archive Exists

Using the Internet Archive's Wayback Machine, I confirmed that community reviews were publicly and easily accessible on Common Sense Media product pages as recently as early 2025. However, these reviews are no longer prominently displayed.

This archive preserves these valuable community perspectives while they remain publicly accessible, documenting firsthand accounts about EdTech tools used in K-12 classrooms.

---

## 🛠️ How It Works

### Two-Stage Process

**Stage 1: URL Collection (Manual)**
- Google search: `site:commonsense.org/node "community review of [product]"`
- JavaScript console script extracts all review URLs
- Saved to text file: `[product]_review_urls.txt`

**Stage 2: Review Scraping (Automated)**
- Python script reads URL list
- Fetches each review page (2-second rate limiting)
- Extracts structured data
- Exports to CSV with timestamp

### Data Collected
- Review title
- Product name
- Date posted
- Full review text
- "My Take" section
- "How I Use It" section
- URL and collection timestamp

---

## 💻 Installation

### Requirements
- Python 3.x
- Safari (for URL collection)

### Setup

1. **Clone this repository:**
```bash
git clone https://github.com/merrybouv/common-sense-review-archive.git
cd common-sense-review-archive
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

### Quick Start

**1. Collect URLs:**
- Search Google: `site:commonsense.org/node "community review of [PRODUCT]"`
- Click "include omitted results"
- Open Safari console (`Cmd + Option + C`)
- Run `console_script.js` (paste and press Enter)
- Save URLs to `[product]_review_urls.txt`

**2. Configure scraper:**
Edit `commonsense_scraper_v3_FINAL.py` line 38:
```python
PRODUCT_NAME = "your_product"  # lowercase, underscores for spaces
```

**3. Run scraper:**
```bash
python commonsense_scraper_v3_FINAL.py
```

**4. Output:**
`commonsense_[product]_YYYYMMDD_HHMMSS.csv`

### Detailed Instructions

See WORKFLOW_QUICK_REFERENCE.md for step-by-step guide.

---

## 📜 License

- **Code:** MIT License
- **Data:** CC BY 4.0 (Creative Commons Attribution)

You are free to use, share, and adapt with attribution.

---

## 🤝 Contributing

This is an active research project. Contributions welcome:

- **Bug reports:** Open an issue
- **Feature requests:** Open an issue
- **Code improvements:** Submit a pull request
- **Additional products:** Contact meredith@netlabconsulting.net

---

## 📬 Contact

**Meredith Bouvier, PhD**
- Email: meredith@netlabconsulting.net
- Organization: NET Lab, Inc. (Delaware Public Benefit Corporation)
- Website: netlabconsulting.net

---

## 🙏 Acknowledgments

Built with [Claude AI](https://claude.ai) by Anthropic.

Special thanks to the Common Sense Education community members who contributed these reviews over the past decade.

---

## ⚖️ Ethical Considerations

**Public Data:** All reviews were publicly accessible on Common Sense Media at time of collection. No authentication or login required.

**Attribution:** Original URLs preserved in dataset. Common Sense Media credited as source platform.

**Purpose:** Academic research on educational technology. No commercial use.

**Respectful Practice:** Rate limiting implemented. User-Agent identifies research purpose. No attempts to access restricted content.

---

## 📚 Citation

If you use this dataset in research or reporting:

```
Bouvier, M. (2026). Common Sense Education Community Review Archive. 
Open Science Framework. https://osf.io/ehbfv/
Code: https://github.com/[YOUR_USERNAME]/common-sense-review-archive
```

---

## 🔄 Updates

This archive is actively maintained. New products added approximately 3 per week.

**Last Updated:** February 16 2026

**Version:** 1.0
