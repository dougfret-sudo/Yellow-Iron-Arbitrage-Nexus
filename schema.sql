-- Yellow Iron Arbitrage Nexus: Master Schema
CREATE TABLE IF NOT EXISTS machinery_inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category VARCHAR(50),                -- 'Track Hoe', 'Dozer', 'Grader', 'Pay Loader'
    make_model VARCHAR(100) NOT NULL,
    listed_price DECIMAL(12, 2),
    machine_hours INT,                   -- Tracking "Particulars"
    serial_prefix VARCHAR(10),           -- Tracking "Particulars"
    location_state VARCHAR(50),
    source_url TEXT UNIQUE,              -- Prevent duplicate alerts
    description TEXT,
    is_private_seller BOOLEAN DEFAULT FALSE,
    is_deal BOOLEAN DEFAULT FALSE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Priority View: Under $100k and NON-CORPORATE
CREATE VIEW IF NOT EXISTS nexus_priority_deals AS
SELECT * FROM machinery_inventory
WHERE listed_price < 100000
AND is_private_seller = TRUE
ORDER BY scanned_at DESC;
