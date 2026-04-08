import asyncio
import sqlite3
import schedule
import time
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
MAX_PRICE = 100000
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
PRIVATE_INDICATORS = ["OBO", "Or Best Offer", "Retiring", "Must sell", "Retired", "Personal use"]

# Local Michigan FSBO URLs
SEARCH_URLS = [
    "https://craigslist.org",
    "https://craigslist.org",
    "https://craigslist.org",
    "https://craigslist.org"
]

def is_private_deal(text):
    text = text.lower()
    # If it looks like a dealer template, reject it
    if any(flag in text for flag in ["financing available", "stock number", "view our inventory"]):
        return False
    return any(k.lower() in text for k in PRIVATE_INDICATORS)

async def save_to_nexus(data):
    conn = sqlite3.connect('nexus.db')
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO machinery_inventory 
            (category, make_model, listed_price, source_url, description, is_private_seller, is_deal)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (data['category'], data['title'], data['price'], data['url'], data['desc'], data['is_private'], True))
        conn.commit()
        print(f"✅ Logged: {data['title']} - ${data['price']}")
    except sqlite3.IntegrityError:
        pass 
    conn.close()

async def scan_market():
    print(f"🔍 Scan Started at {time.strftime('%X')}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in SEARCH_URLS:
            await page.goto(url)
            await page.wait_for_timeout(2000)
            soup = BeautifulSoup(await page.content(), 'html.parser')
            for item in soup.select('.result-row'):
                try:
                    title = item.select_one('.result-title').text
                    price = int(item.select_one('.result-price').text.replace('$', '').replace(',', ''))
                    link = item.select_one('a')['href']
                    category = next((a for a in TARGET_ASSETS if a.lower() in title.lower()), "Other")
                    if category != "Other" and price < MAX_PRICE:
                        await save_to_nexus({
                            'category': category, 'title': title, 'price': price,
                            'url': link, 'desc': title, 'is_private': is_private_deal(title)
                        })
                except: continue
        await browser.close()
    print("💤 Scan Complete. Sleeping until next scheduled time.")

# Function to run the async scraper inside the scheduler
def job():
    asyncio.run(scan_market())

if __name__ == "__main__":
    print("🚀 Yellow Iron Nexus: Daily Tracker Online")
    # Schedule to run once a day at 8:00 AM
    schedule.every().day.at("08:00").do(job)
    
    # Run once immediately on startup
    job()

    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute if it's time to run
  
