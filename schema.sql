-- 1. Create the main tracking table
CREATE TABLE IF NOT EXISTS machinery_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50),                -- 'Track Hoe', 'Dozer', etc.
    make_model VARCHAR(100) NOT NULL,
    listed_price DECIMAL(12, 2),
    machine_hours INT,
    location_state VARCHAR(2),
    source_url TEXT UNIQUE,              -- Prevents duplicates
    description TEXT,
    is_deal BOOLEAN DEFAULT FALSE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create a View for sub-100k deals from non-corporate sources
CREATE OR REPLACE VIEW private_yellow_iron_deals AS
SELECT *
FROM machinery_inventory
WHERE listed_price < 100000
  AND is_deal = TRUE
  AND (
    source_url LIKE '%facebook.com%' 
    OR source_url LIKE '%craigslist.org%'
    OR (
        source_url NOT LIKE '%ritchiebros.com%'
        AND source_url NOT LIKE '%ironplanet.com%'
        AND source_url NOT LIKE '%cat.com%'
        AND source_url NOT LIKE '%deere.com%'
    )
  );
