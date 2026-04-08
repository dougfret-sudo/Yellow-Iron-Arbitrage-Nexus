# --- Private/Small Seller Configuration ---
TARGET_ASSETS = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
MAX_PRICE = 100000

# High-intent private seller keywords
PRIVATE_INDICATORS = [
    "OBO", "Or Best Offer", "Retiring", "Must sell", 
    "Cash only", "Individual", "Retired", "Personal use",
    "Negotiable", "No dealers", "Local pickup"
]

def is_private_listing(data):
    """
    Identifies a private listing by checking for 'individual' 
    keywords and avoiding dealer-specific patterns.
    """
    text = f"{data.get('title', '')} {data.get('description', '')}".lower()
    
    # 1. Reject if it mentions a 'Dealer' or 'Inventory' (Large Dealership typicals)
    if any(x in text for x in ["financing available", "visit our website", "stock number"]):
        return False
        
    # 2. Check for private seller language
    return any(word.lower() in text for word in PRIVATE_INDICATORS)

def run_nexus_search():
    # Example logic: Scan sources like Craigslist or FB Groups
    listings = fetch_listings_from_source() 
    for item in listings:
        if item['price'] < MAX_PRICE and is_private_listing(item):
            # Check if it matches your specific equipment types
            if any(asset.lower() in item['title'].lower() for asset in TARGET_ASSETS):
                save_to_db(item)
                print(f"🔥 Private Deal Found: {item['title']} - ${item['price']}")
