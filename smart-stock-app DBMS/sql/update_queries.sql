-- Update an item
UPDATE Item 
SET name = ?, qty = ?, price = ?
WHERE item_code = ?;