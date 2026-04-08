-- Flag deals that are under $100k and likely private
UPDATE machinery_inventory 
SET is_deal = TRUE 
WHERE listed_price < 100000 
AND (source_url LIKE '%facebook.com%' OR source_url LIKE '%craigslist.org%');
