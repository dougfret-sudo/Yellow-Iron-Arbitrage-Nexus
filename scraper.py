import asyncio
import sqlite3
import schedule
import time
import smtplib
from email.message import EmailMessage
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# --- CONFIGURATION ---
MAX_PRICE = 100000
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
PRIVATE_KEYWORDS = ["OBO", "Or Best Offer", "Retiring", "Must sell", "Retired", "Personal use"]

# --- EMAIL SETTINGS ---
# For Gmail: Use an "App Password," not your regular login password.
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password" 
EMAIL_RECEIVER = "your-receiving-email@gmail.com"

# Local Michigan FSBO URLs
SEARCH_URLS = [
    "https://craigslist.org",
    "https://craigslist.org",
    "https://craigslist.org",
    "https://craigslist.org"
]

def send_nexus_email(data):
    """Sends a formatted email with a clickable link."""
    msg = EmailMessage()
    msg.set_content(f"""
    🔥 YELLOW IRON NEXUS: PRIVATE DEAL FOUND 🔥
    
    Asset: {data['title']}
    Price: ${data['price']}
    Category: {data['category']}
    
    Link to Listing: {data['url']}
    
    Description Preview: 
    {data['desc']}
    
    -- Automated Nexus Alert --
    """)

    msg['Subject'] = f"NEXUS ALERT: {data['category']} - ${data['price']}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL('://gmail.com', 465) as smtp:
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
        
        # Only send email for high-priority private deals
        if data['is_private']:
            send_nexus_email(data)
            
    except sqlite3.IntegrityError:
        pass # Already in DB
    finally:
        conn.close()

async def scan_market():
    print(f"🔍 Scan Started: {time.strftime('%X')}")
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
                        await save_and_alert({
                            'category': category, 'title': title, 'price': price,
                            'url': link, 'desc': title, 'is_private': is_private_deal(title)
                        })
                except: continue
        await browser.close()

def job():
    asyncio.run(scan_market())

if __name__ == "__main__":
    print("🚀 Nexus Engine: Daily Email Tracker Active (08:00 AM)")
    schedule.every().day.at("08:00").do(job)
    
    # Run once immediately to verify everything works
    job() 

    while True:
        schedule.run_pending()
        time.sleep(60)
