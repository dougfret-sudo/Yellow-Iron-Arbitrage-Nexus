import requests
from bs4 import BeautifulSoup
import sqlite3

# --- CONFIGURATION ---
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
MAX_PRICE = 100000
PRIVATE_KEYWORDS = ["OBO", "Or Best Offer", "Retiring", "Must move", "Cash only", "Retired"]

def is_small_seller(text):
    """Filters for private seller language and rejects corporate templates."""
    text = text.lower()
    if any(x in text for x in ["financing available", "stock number", "view our inventory"]):
        return False
    return any(keyword.lower() in text for keyword in PRIVATE_KEYWORDS)

def save_to_db(data):
    """Saves findings to the SQL database."""
    conn = sqlite3.connect('nexus.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO machinery_inventory (category, make_model, listed_price, source_url, description, is_deal)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['category'], data['title'], data['price'], data['url'], data['desc'], True))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Skip duplicates
    finally:
        conn.close()

def run_scraper(url):
    """Example scraper for a marketplace (e.g., Craigslist)"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # This part varies by website; it finds the listings on the page
    for listing in soup.select('.result-row'): 
        title = listing.select_one('.result-title').text
        price = int(listing.select_one('.result-price').text.replace('$', '').replace(',', ''))
        desc = listing.select_one('.description-preview').text # Hypothetical selector
        link = listing.select_one('a')['href']
        
        # --- THE NEXUS FILTER ---
        if price < MAX_PRICE and is_small_seller(desc):
            # Verify if it's one of your four target equipment types
            category_match = next((a for a in TARGET_ASSETS if a.lower() in title.lower()), None)
            if category_match:
                save_to_db({
                    'category': category_match,
                    'title': title,
                    'price': price,
                    'url': link,
                    'desc': desc
                })
                print(f"🔥 NEXUS ALERT: {title} for ${price}")

if __name__ == "__main__":
    # Add your targeted FSBO search URLs here
    run_scraper("https://craigslist.org") 
