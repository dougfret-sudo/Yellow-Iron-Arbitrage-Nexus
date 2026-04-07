-- Yellow Iron Nexus: Asset Tracking Schema
CREATE TABLE machinery_inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make_model VARCHAR(100) NOT NULL,    -- e.g., 'CAT 320BL'
    serial_prefix VARCHAR(10),           -- Important for "Particulars"
    listed_price DECIMAL(12, 2),
    machine_hours INT,
    location_state VARCHAR(2),           -- Logic: Is it near a port for Dubai?
    source_url TEXT,
    is_deal BOOLEAN DEFAULT FALSE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
