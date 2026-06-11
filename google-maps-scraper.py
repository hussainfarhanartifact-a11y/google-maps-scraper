# ============================================================
#  Google Maps Business Scraper — by Hussain Farhan
#
#  Searches Google Maps for businesses by keyword + location
#  Extracts: name, rating, reviews, category, address,
#            phone number, website
#  Saves results to google_maps_data.csv
#
#  Requirements:
#    pip install selenium webdriver-manager
# ============================================================

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
from datetime import date


# ── SETTINGS ─────────────────────────────────────────────────
SEARCH_QUERY  = "restaurants in Karachi"   # ← change this
MAX_RESULTS   = 20                          # ← how many businesses to scrape
OUTPUT_FILE   = "google_maps_data.csv"
# ─────────────────────────────────────────────────────────────


def create_driver():
    """Set up a headless Chrome browser (runs in background, no window)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")           # run without opening a window
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=en")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def search_google_maps(driver, query):
    """Open Google Maps and search for the given query."""
    print(f"🔍 Searching Google Maps for: {query}")
    driver.get("https://www.google.com/maps")
    wait = WebDriverWait(driver, 10)

    # Type into the search box and hit Enter
    search_box = wait.until(EC.presence_of_element_located((By.ID, "searchboxinput")))
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)


def scroll_results(driver, max_results):
    """Scroll the results panel to load more listings."""
    print(f"📜 Loading up to {max_results} results...")
    try:
        results_panel = driver.find_element(
            By.CSS_SELECTOR, "div[role='feed']"
        )
        last_count = 0
        for _ in range(max_results // 5 + 5):
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                results_panel
            )
            time.sleep(2)
            listings = driver.find_elements(
                By.CSS_SELECTOR, "a.hfpxzc"
            )
            if len(listings) >= max_results:
                break
            if len(listings) == last_count:
                break
            last_count = len(listings)
    except Exception as e:
        print(f"  Scroll warning: {e}")


def get_text_safe(driver, css_selector, default="N/A"):
    """Try to get text from an element, return default if not found."""
    try:
        el = driver.find_element(By.CSS_SELECTOR, css_selector)
        return el.text.strip()
    except:
        return default


def get_attr_safe(driver, css_selector, attr, default="N/A"):
    """Try to get an attribute from an element, return default if not found."""
    try:
        el = driver.find_element(By.CSS_SELECTOR, css_selector)
        return el.get_attribute(attr).strip()
    except:
        return default


def scrape_business_details(driver):
    """
    Scrape details from an open business panel on the right side.
    Returns a dict of business info.
    """
    time.sleep(2)  # wait for panel to load

    # Business name
    name = get_text_safe(driver, "h1.DUwDvf")

    # Rating (e.g. "4.5")
    rating = get_text_safe(driver, "div.F7nice span[aria-hidden='true']")

    # Number of reviews (e.g. "1,234 reviews")
    reviews = get_text_safe(driver, "div.F7nice span[aria-label*='reviews']")

    # Category (e.g. "Pakistani restaurant")
    category = get_text_safe(driver, "button.DkEaL")

    # Address
    address = get_text_safe(
        driver,
        "button[data-item-id='address'] div.Io6YTe"
    )

    # Phone number
    phone = get_text_safe(
        driver,
        "button[data-item-id*='phone'] div.Io6YTe"
    )

    # Website
    website = get_attr_safe(
        driver,
        "a[data-item-id='authority']",
        "href"
    )

    return {
        "name":       name,
        "rating":     rating,
        "reviews":    reviews,
        "category":   category,
        "address":    address,
        "phone":      phone,
        "website":    website,
        "date_scraped": date.today()
    }


def scrape_all_businesses(query, max_results=20):
    """Main function — searches Maps, scrapes each listing, returns list."""
    driver = create_driver()
    results = []

    try:
        search_google_maps(driver, query)
        scroll_results(driver, max_results)

        # Collect all listing links
        listings = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
        listings = listings[:max_results]
        print(f"Found {len(listings)} listings. Scraping details...\n")

        for i, listing in enumerate(listings):
            try:
                name_preview = listing.get_attribute("aria-label") or f"Business {i+1}"
                print(f"  [{i+1}/{len(listings)}] {name_preview}")

                # Click listing to open its detail panel
                driver.execute_script("arguments[0].click();", listing)
                time.sleep(2)

                business = scrape_business_details(driver)
                results.append(business)

                # Print a quick preview
                print(f"         ⭐ {business['rating']}  📍 {business['address'][:40]}")

            except Exception as e:
                print(f"  ⚠️  Skipped listing {i+1}: {e}")
                continue

    finally:
        driver.quit()

    return results


def save_to_csv(data, filename=OUTPUT_FILE):
    """Save results to CSV file."""
    if not data:
        print("No data to save.")
        return

    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

    print(f"\n✅ Saved {len(data)} businesses to '{filename}'")


# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Google Maps Scraper — by Hussain Farhan")
    print("=" * 50 + "\n")

    data = scrape_all_businesses(SEARCH_QUERY, MAX_RESULTS)
    save_to_csv(data)

    # Preview top 3
    print("\n📋 Sample results:")
    for biz in data[:3]:
        print(f"\n  🏢 {biz['name']}")
        print(f"     ⭐ Rating   : {biz['rating']}  ({biz['reviews']})")
        print(f"     🏷️  Category : {biz['category']}")
        print(f"     📍 Address  : {biz['address']}")
        print(f"     📞 Phone    : {biz['phone']}")
        print(f"     🌐 Website  : {biz['website']}")
