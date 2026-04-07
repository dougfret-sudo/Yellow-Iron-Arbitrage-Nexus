# Simplified Logic for the Scraper Engine
# Goal: Target specific "Yellow Iron" specs.

target_machines = ["Caterpillar 320BL", "Komatsu PC210", "Deere 350G"]
max_price = 45000  # Example "Deal" threshold

def check_for_deals(listing):
    for machine in target_machines:
        if machine in listing.title and listing.price <= max_price:
            send_alert_to_texas(listing)
            save_to_sql_nexus(listing)
