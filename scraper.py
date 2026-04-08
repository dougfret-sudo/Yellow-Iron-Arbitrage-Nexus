import asyncio
import sqlite3
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# --- TARGET CONFIGURATION ---
MAX_PRICE = 100000
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
PRIVATE_INDICATORS = ["OBO", "Or Best Offer", "Retiring", "Must sell", "Retired", "Personal use"]

# Add targeted search URLs here
SEARCH_URLS = [
    "https://craigslist.org",
    "https://craigslist.org"
]

def is_private_deal(text):
    """Rejects large dealer templates, accepts 'OBO' and personal language."""
    text = text.lower()
    corporate_red_flags = ["financing available", "stock number", "view our inventory", "ritchie bros"]
    if any(flag in text for flag in corporate_red_flags):
        return False
    return any(k.lower() in text for k in PRIVATE_INDICATORS)

async def save_to_nexus(data):
    """Database insertion with conflict resolution."""
    conn = sqlite3.connect('nexus.db')
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO machinery_inventory 
            (category, make_model, listed_price, source_url, description, is_private_seller, is_deal)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (data['category'], data['title'], data['price'], data['url'], data['desc'], data['is_private'], True))
        conn.commit()
        if data['is_private']:
            print(f"🔥 PRIVATE DEAL ALERT: {data['title']} - ${data['price']}")
    except sqlite3.IntegrityError:
        pass # Already tracked
    conn.close()

async def run_nexus():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for url in SEARCH_URLS:
            print(f"Scanning: {url}")
            await page.goto(url)
            await page.wait_for_timeout(2000)
            soup = BeautifulSoup(await page.content(), 'html.parser')
            
            for item in soup.select('.result-row'):
                try:
                    title = item.select_one('.result-title').text
                    price_text = item.select_one('.result-price').text
                    price = int(price_text.replace('$', '').replace(',', ''))
                    link = item.select_one('a')['href']
                    
                    # Match against your 4 specific categories
                    category = next((a for a in TARGET_ASSETS if a.lower() in title.lower()), "Other")
                    
                    if category != "Other" and price < MAX_PRICE:
                        is_private = is_private_deal(title)
                        await save_to_nexus({
                            'category': category, 'title': title, 'price': price,
                            'url': link, 'desc': title, 'is_private': is_private
                        })
                except: continue
        await browser.close()

if __name__ == "__main__":
    print("🚀 Nexus Arbitrage Engine Online...")
    asyncio.run(run_nexus())
  
