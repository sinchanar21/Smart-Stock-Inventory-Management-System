-- Get all items
SELECT * FROM Item;

-- Get specific item by ID
SELECT * FROM Item WHERE item_code = ?;

-- Get audit trail
SELECT * FROM AuditTrail ORDER BY operation_timestamp DESC;

-- Get transactions for an item
SELECT * FROM StockTransaction WHERE item_code = ? ORDER BY transaction_date DESC;

-- Get sales records with item names
SELECT s.*, i.name as item_name FROM Sales s
JOIN Item i ON s.item_code = i.item_code
ORDER BY s.date DESC;

-- Get stock records with item names
SELECT s.*, i.name as item_name FROM Stock s
JOIN Item i ON s.item_code = i.item_code
ORDER BY s.location;

-- Search items
SELECT * FROM Item WHERE name LIKE ? OR item_code LIKE ? ORDER BY name;

-- Verify user
SELECT * FROM Admin WHERE username = ? AND password = ?;

-- Check if admin exists
SELECT COUNT(*) FROM Admin;

-- Check if username exists
SELECT COUNT(*) FROM Admin WHERE username = ?;

-- Check if item name exists
SELECT COUNT(*) FROM Item WHERE name = ?;

-- Check if another item with same name exists (during update)
SELECT COUNT(*) FROM Item WHERE name = ? AND item_code != ?;

-- Get item names and quantities for chart
SELECT name, qty FROM Item;