# Google Maps Local Lead Finder

A robust, local-first lead generation tool that searches Google Maps for business listings and extracts publicly visible information, specifically targeting actual websites, emails (if visible), and phone numbers. It operates using Playwright for browser automation, guaranteeing no dependency on the Google Maps API and maximizing result harvesting through deep scrolling.

## Features

- **No API Keys Required:** Uses Playwright browser automation.
- **Maximum Realistic Results:** Employs intelligent scrolling and lazy-loading detection to gather all available listings instead of just the first page.
- **Bulk Location Processing:** Enter a single keyword and multiple locations; the tool processes them sequentially, ensuring stability and avoiding blocks.
- **Deduplication:** Automatically removes duplicates across locations based on Place ID, domain, phone number, and normalized business name.
- **Resilience:** Jobs run in a background thread and intermediate progress is incrementally saved, ensuring data isn't lost during long runs.
- **Excel/Sheets Ready:** Direct one-click TSV copying allows immediate pasting into Excel or Google Sheets. JSON and CSV downloads are also supported.
- **Modern UI:** Clean, responsive interface featuring real-time scraping progress updates.

## Installation

### Prerequisites
- Python 3.8+
- Windows (Local usage recommended)

### 1. Clone or Copy the Repository
Navigate to the project folder:
```bash
cd google-maps-lead-finder
```

### 2. Install Requirements
Create a virtual environment (optional but recommended):
```bash
python -m venv venv
venv\Scripts\activate
```

Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers
Install the Chromium browser used by Playwright:
```bash
playwright install chromium
```

### 4. Configuration
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Adjust the variables if needed. By default, the UI allows you to toggle Headless mode on or off.

## Running the Application

Start the Flask server:
```bash
python app.py
```
Open your web browser and go to:
`http://127.0.0.1:5000`

## Usage: AC Repair Test

1. Open `http://127.0.0.1:5000`.
2. In the **Keyword** field, enter: `AC Repair`
3. In the **Locations** field, enter: `Dallas, Fort Worth, Austin, Addison, Pflugerville`
4. Make sure "Headless Browser" is unchecked if you want to watch the browser work (recommended for debugging).
5. Click **START SEARCH**.
6. The app will navigate to each location sequentially, scroll to find all lazy-loaded results, and save them. You'll see real-time progress on the UI.
7. Once finished, click **COPY FULL DATA** and paste it directly into Excel.

## Data Storage

All data is saved locally to avoid data loss on crashes:
- Active Jobs and Results: `data/jobs/<job_id>/` (contains `progress.json`, `results.json`, and `results.csv`)
- Search History: `data/history/`

## Troubleshooting

- **Google Maps Selector Changes:** If Google Maps updates their UI and the scraper stops extracting correctly, inspect the live DOM. Open `scraper/result_extractor.py` and update the XPath or CSS selectors (like `extract_business_name` or `extract_website`).
- **Google Maps Requires Verification / CAPTCHA:** If running locally in headful mode (`Headless` unchecked), you can manually solve the CAPTCHA in the automated browser window. Once solved, the scraper will continue.
- **No Results Loading:** Ensure your network is stable and you haven't been temporarily rate-limited by Google Maps for excessive scraping. Add a delay (`SCROLL_PAUSE` in `.env`) to slow down requests.
