-- Create Admin table
CREATE TABLE IF NOT EXISTS Admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
);

-- Create Item table
CREATE TABLE IF NOT EXISTS Item (
    item_code INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    qty INTEGER,
    price REAL,
    admin_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES Admin(admin_id)
);

-- Create Sales table
CREATE TABLE IF NOT EXISTS Sales (
    sales_code INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    item_code INTEGER,
    FOREIGN KEY (item_code) REFERENCES Item(item_code)
);

-- Create StockTransaction table
CREATE TABLE IF NOT EXISTS StockTransaction (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_code INTEGER,
    qty INTEGER,
    type TEXT,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_code) REFERENCES Item(item_code)
);

-- Create Stock table
CREATE TABLE IF NOT EXISTS Stock (
    location TEXT,
    item_code INTEGER,
    qty INTEGER,
    FOREIGN KEY (item_code) REFERENCES Item(item_code)
);

-- Create AuditTrail table
CREATE TABLE IF NOT EXISTS AuditTrail (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT,
    table_name TEXT,
    record_id INTEGER,
    old_values TEXT,
    new_values TEXT,
    operation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);