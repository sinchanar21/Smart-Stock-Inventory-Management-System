-- Insert a new admin
INSERT INTO Admin (username, password) VALUES (?, ?);

-- Insert a new item
INSERT INTO Item (name, qty, price, admin_id) VALUES (?, ?, ?, ?);

-- Insert a sales record
INSERT INTO Sales (date, item_code) VALUES (?, ?);

-- Insert a stock record
INSERT INTO Stock (location, item_code, qty) VALUES (?, ?, ?);

-- Insert a stock transaction
INSERT INTO StockTransaction (item_code, qty, type, transaction_date) 
VALUES (?, ?, ?, CURRENT_TIMESTAMP);

-- Insert an audit trail entry
INSERT INTO AuditTrail (operation_type, table_name, record_id, old_values, new_values)
VALUES (?, ?, ?, ?, ?);