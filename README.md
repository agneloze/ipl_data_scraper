
# ipl_data_scraper

A collection of Python-based web scrapers designed to extract comprehensive IPL player career statistics (batting and bowling) directly from official data sources. These scripts bypass standard HTML scraping where possible to fetch data from underlying JSON feeds for higher accuracy.

## Features

* **Career Totals:** Extracts "All-Time" career stats, including runs, strike rates, wickets, economy, and more.
* **Dual-Mode Scraping:** Choose between fully automated bulk scraping or targeted manual scraping.
* **Excel Export:** Automatically generates formatted `.xlsx` files for easy data analysis.
* **Smart Parsing:** Handles JavaScript-wrapped JSON responses and cleans player naming conventions.

---

##  Script Overviews

### 1. Fully Automated Scraper (`ipl_auto_all.py`)

This is the "set it and forget it" tool.

* **How it works:** It visits the official IPL team pages for all 10 franchises, extracts every unique player ID currently listed in the squads, and then fetches their career statistics.
* **Best for:** Building a complete database of current IPL players without manual input.
* **Output:** `IPL_All_Players_Stats.xlsx`

### 2. Targeted Career Scraper (`ipl_career_stats.py`)

This tool is designed for precision.

* **How it works:** You provide a specific list of IPL player profile URLs. The script extracts the IDs from those URLs and fetches data only for those individuals.
* **Best for:** Comparing specific players or updating stats for a small, custom list.
* **Output:** `IPL_Career_Stats.xlsx`

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name

```


2. **Install dependencies:**
This project requires `pandas`, `requests`, `beautifulsoup4`, and `openpyxl` (for Excel support).
```bash
pip install pandas requests beautifulsoup4 openpyxl

```



---

##  How to Use

### Running the Automated Scraper

Simply run the script. It will navigate through all teams automatically:

```bash
python ipl_auto_all.py

```

### Running the Targeted Scraper

1. Open `ipl_career_stats.py` in your code editor.
2. Locate the `PLAYER_URLS` list at the top of the file.
3. Paste the URLs of the players you want to scrape:
```python
PLAYER_URLS = [
    "https://www.iplt20.com/players/ms-dhoni/1",
    "https://www.iplt20.com/players/virat-kohli/164",
]

```


4. Run the script:
```bash
python ipl_career_stats.py

```



---

## Important Notes

* **Rate Limiting:** Both scripts include `time.sleep()` delays. Please do not remove these, as they prevent your IP from being flagged or blocked by the server.
* **Data Source:** This tool fetches data from the S3 buckets used by the official IPL site. If the site structure changes, the regex patterns in the scripts may need updating.

---
