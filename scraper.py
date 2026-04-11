import os
import asyncio
import sqlite3
import schedule
import time
import smtplib
from email.message import EmailMessage
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load secrets from your local .env (Keep this off GitHub!)
load_dotenv()

# --- CONFIGURATION ---
MAX_PRICE = 100000
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
PRIVATE_KEYWORDS = ["OBO", "Or Best Offer", "Retiring", "Must sell", "Retired", "Personal use"]

# --- SECURE EMAIL SETTINGS ---
EMAIL_SENDER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_TARGET")

# Local Michigan FSBO URLs (Ensure these are full links)
SEARCH_URLS = [
    "https://craigslist.org",
    "https://craigslist.org"
]

def init_vault():
    """Ensures the database exists with the correct columns before scraping."""
    conn = sqlite3.connect('nexus.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS machinery_inventory 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, make_model TEXT, 
         listed_price REAL, source_url TEXT UNIQUE, description TEXT, 
         is_private_seller BOOLEAN, is_deal BOOLEAN, scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()

def send_nexus_email(data):
    msg = EmailMessage()
    msg.set_content(f"Asset: {data['title']}\nPrice: ${data['price']}\nLink: {data['url']}")
    msg['Subject'] = f"🔥 NEXUS ALERT: {data['category']} - ${data['price']}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        # FIXED: Corrected Gmail SMTP address
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"📧 Email Sent for: {data['title']}")
    except Exception as e:
        print(f"❌ Email Failed: {e}")

def is_private_deal(text):
    text = text.lower()
    if any(flag in text for flag in ["financing available", "stock number", "view our inventory"]):
        return False
    return any(k.lower() in text for k in PRIVATE_KEYWORDS)

async def save_and_alert(data):
    conn = sqlite3.connect('nexus.db')
    cur = conn.cursor()
    try:
        cur.execute('''INSERT INTO machinery_inventory 
            (category, make_model, listed_price, source_url, description, is_private_seller, is_deal)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', 
            (data['category'], data['title'], data['price'], data['url'], data['desc'], data['is_private'], True))
        conn.commit()
        if data['is_private']:
            send_nexus_email(data)
    except sqlite3.IntegrityError:
        pass 
    finally:
        conn.close()

async def scan_market():
    print(f"🔍 Scan Started: {time.strftime('%X')}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        for url in SEARCH_URLS:
            try:
                await page.goto(url, timeout=60000)
                soup = BeautifulSoup(await page.content(), 'html.parser')
                # Note: Craigslist often uses 'li.cl-static-standard-browse-card' or similar now
                for item in soup.select('.result-row'): 
                    title = item.select_one('.result-title').text
                    price = int(item.select_one('.result-price').text.replace('$', '').replace(',', ''))
                    link = item.select_one('a')['href']
                    category = next((a for a in TARGET_ASSETS if a.lower() in title.lower()), "Other")
                    
                    if category != "Other" and price < MAX_PRICE:
                        await save_and_alert({
                            'category': category, 'title': title, 'price': price,
                            'url': link, 'desc': title, 'is_private': is_private_deal(title)
                        })
            except Exception as e:
                print(f"⚠️ Error on {url}: {e}")
        await browser.close()

def job():
    init_vault() # Build the table first
    asyncio.run(scan_market())

if __name__ == "__main__":
    print("🚀 Nexus Engine Active. Testing Saturday 08:00 AM.")
    schedule.every().day.at("08:00").do(job)
    job() # Run once on start
    while True:
        schedule.run_pending()
        time.sleep(60)
