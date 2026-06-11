# Google Maps Business Scraper
**By Hussain Farhan**

Searches Google Maps for any keyword and location and scrapes full business details — name, rating, reviews, address, phone number, and website. Exports everything to a clean CSV file.

## What it does
- Search any keyword and location (e.g. "dentists in Dubai", "gyms in Karachi")
- Automatically scrolls to load more results
- Extracts name, rating, reviews, category, address, phone, website
- Exports to google_maps_data.csv
- Runs headless — no browser window needed

## How to run

Install dependencies:
pip install selenium webdriver-manager

Edit the search at the top of the file:
SEARCH_QUERY = "restaurants in Karachi"
MAX_RESULTS  = 20

Run it:
python google_maps_scraper.py

## Output
| name | rating | reviews | address | phone | website |
|------|--------|---------|---------|-------|---------|
| Kolachi | 4.3 | 2,847 | Do Darya... | +92 21... | kolachi.com |

## Tech used
Python · Selenium · webdriver-manager

## Hire me
📧 hussainfarhanartifact@gmail.com
🌐 Fiverr: fiverr.com/hussainfarhan_d
