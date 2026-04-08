# --- Scraper Configuration ---
CATEGORIES = ["Track Hoe", "Dozer", "Grader", "Pay Loader"]
MAX_PRICE = 100000

# Hallmarks of a private/small dealer listing
PRIVATE_KEYWORDS = [
    "OBO", "Or Best Offer", "Retiring", "Must move", 
    "Cash only", "Private sale", "Individual", "Retired"
]

# TARGET LIST: Focus on these models known to hit <$100k in private sales
TARGETS = {
    "Track Hoe": ["CAT 320", "Deere 160G", "Komatsu PC210", "Hitachi ZX"],
    "Dozer": ["CAT D3", "CAT D5", "Deere 650", "Case 850"],
    "Grader": ["CAT 12G", "CAT 140G", "Deere 670"],
    "Pay Loader": ["CAT 924", "Deere 544", "Case 621"]
}

def is_private_deal(description):
    """
    Filters for private seller language. 
    Big dealers use corporate templates; individuals use 'OBO' and 'Retired'.
    """
    return any(word.lower() in description.lower() for word in PRIVATE_KEYWORDS)

def process_listing(listing):
    price = listing.get('price', 0)
    description = listing.get('description', "")
    
    # Nexus Trigger: Under $100k + Private Seller Keywords
    if price < MAX_PRICE and is_private_deal(description):
        save_to_nexus(listing)
        send_alert(listing)
