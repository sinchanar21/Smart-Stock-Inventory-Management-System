import sqlite3

# This file is no longer used for CRUD operations in the Flask app
# All database operations are now handled directly in app.py using SQL files
# Keeping this file for potential future use or standalone scripts

import sqlite3

def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect('smartstock.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with all required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load and execute schema from SQL file
    schema_sql = load_sql_query('create_tables.sql')
    # Split by semicolon and execute each statement
    for statement in schema_sql.split(';'):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)

    conn.commit()
    conn.close()
    
    # Create default admin if needed
    create_default_admin()

def log_audit(operation_type, table_name, record_id, old_values=None, new_values=None):
    """Log an audit trail entry for database operations"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load SQL query from file
    queries = load_sql_query('insert_queries.sql').split(';')
    audit_query = None
    for query in queries:
        query = query.strip()
        if query and 'AuditTrail' in query:
            audit_query = query
            break
    
    if audit_query:
        cursor.execute(audit_query, (operation_type, table_name, record_id, 
              json.dumps(old_values) if old_values else None,
              json.dumps(new_values) if new_values else None))
    
    conn.commit()
    conn.close()

def get_all_items():
    """Retrieve all items from the database"""
    conn = get_db_connection()
    query = load_sql_query('read_queries.sql').split(';')[0].strip()  # Get first query
    items = conn.execute(query).fetchall()
    conn.close()
    return items

def get_item_by_id(item_id):
    """Retrieve a specific item by its ID"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    item_query = queries[1].strip()  # Get second query
    item = conn.execute(item_query, (item_id,)).fetchone()
    conn.close()
    return item

def create_item(name, qty, price, admin_id=1):
    """Create a new item in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if an item with the same name already exists
    queries = load_sql_query('read_queries.sql').split(';')
    count_query = queries[10].strip()  # Check if item name exists query
    cursor.execute(count_query, (name,))
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        raise ValueError(f"An item with the name '{name}' already exists.")
    
    # Load insert query from file
    queries = load_sql_query('insert_queries.sql').split(';')
    insert_query = None
    for query in queries:
        query = query.strip()
        if query and 'Item' in query and 'name' in query:
            insert_query = query
            break
    
    if insert_query:
        cursor.execute(insert_query, (name, qty, price, admin_id))
    
    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log the creation
    log_audit('CREATE', 'Item', item_id, None, {
        'name': name, 'qty': qty, 'price': price, 'admin_id': admin_id
    })
    
    return item_id

def update_item(item_id, name, qty, price):
    """Update an existing item in the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if another item with the same name already exists
    queries = load_sql_query('read_queries.sql').split(';')
    count_query = queries[11].strip()  # Check if another item with same name exists
    cursor.execute(count_query, (name, item_id))
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        raise ValueError(f"An item with the name '{name}' already exists.")
    
    # Get old values for audit trail
    old_item = get_item_by_id(item_id)
    old_values = dict(old_item) if old_item else None
    
    # Load update query from file
    update_query = load_sql_query('update_queries.sql')
    cursor.execute(update_query, (name, qty, price, item_id))
    
    conn.commit()
    conn.close()
    
    # Log the update
    log_audit('UPDATE', 'Item', item_id, old_values, {
        'name': name, 'qty': qty, 'price': price
    })

def delete_item(item_id):
    """Delete an item from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get old values for audit trail
    old_item = get_item_by_id(item_id)
    old_values = dict(old_item) if old_item else None
    
    # Load delete query from file
    delete_query = load_sql_query('delete_queries.sql')
    cursor.execute(delete_query, (item_id,))
    conn.commit()
    conn.close()
    
    # Log the deletion
    log_audit('DELETE', 'Item', item_id, old_values, None)

def get_audit_trail():
    """Retrieve all audit trail entries"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    audit_query = queries[2].strip()  # Get audit trail query
    audit_entries = conn.execute(audit_query).fetchall()
    conn.close()
    return audit_entries

def create_stock_transaction(item_id, qty, transaction_type):
    """Create a stock transaction record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load insert query from file
    queries = load_sql_query('insert_queries.sql').split(';')
    transaction_query = None
    for query in queries:
        query = query.strip()
        if query and 'StockTransaction' in query:
            transaction_query = query
            break
    
    if transaction_query:
        cursor.execute(transaction_query, (item_id, qty, transaction_type))
    
    transaction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return transaction_id

def get_item_transactions(item_id):
    """Get all transactions for a specific item"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    transaction_query = queries[3].strip()  # Get item transactions query
    transactions = conn.execute(transaction_query, (item_id,)).fetchall()
    conn.close()
    return transactions

def create_sales_record(date, item_code):
    """Create a sales record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load insert query from file
    queries = load_sql_query('insert_queries.sql').split(';')
    sales_query = None
    for query in queries:
        query = query.strip()
        if query and 'Sales' in query and 'date' in query:
            sales_query = query
            break
    
    if sales_query:
        cursor.execute(sales_query, (date, item_code))
    
    sales_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return sales_id

def get_sales_records():
    """Get all sales records"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    sales_query = queries[4].strip()  # Get sales records query
    sales = conn.execute(sales_query).fetchall()
    conn.close()
    return sales

def create_stock_record(location, item_code, qty):
    """Create a stock record"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Load insert query from file
    queries = load_sql_query('insert_queries.sql').split(';')
    stock_query = None
    for query in queries:
        query = query.strip()
        if query and 'Stock' in query and 'location' in query:
            stock_query = query
            break
    
    if stock_query:
        cursor.execute(stock_query, (location, item_code, qty))
    
    conn.commit()
    conn.close()

def get_stock_records():
    """Get all stock records"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    stock_query = queries[5].strip()  # Get stock records query
    stock = conn.execute(stock_query).fetchall()
    conn.close()
    return stock

def search_items(query):
    """Search for items by name or code"""
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    search_query = queries[6].strip()  # Search items query
    items = conn.execute(search_query, (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return items

def verify_user(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    queries = load_sql_query('read_queries.sql').split(';')
    verify_query = queries[7].strip()  # Verify user query
    cursor.execute(verify_query, (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def create_default_admin():
    """Create a default admin user if none exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if any admin exists
    queries = load_sql_query('read_queries.sql').split(';')
    count_query = queries[8].strip()  # Check if admin exists query
    cursor.execute(count_query)
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Load insert query from file
        queries = load_sql_query('insert_queries.sql').split(';')
        admin_query = None
        for q in queries:
            q = q.strip()
            if q and 'Admin' in q and 'username' in q:
                admin_query = q
                break
        
        if admin_query:
            cursor.execute(admin_query, ('admin', 'password'))
        
        conn.commit()
    
    conn.close()

def create_user(username, password):
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if username already exists
    queries = load_sql_query('read_queries.sql').split(';')
    count_query = queries[9].strip()  # Check if username exists query
    cursor.execute(count_query, (username,))
    count = cursor.fetchone()[0]
    
    if count > 0:
        conn.close()
        raise ValueError(f"Username '{username}' already exists.")
    
    # Create new user
    queries = load_sql_query('insert_queries.sql').split(';')
    user_query = None
    for q in queries:
        q = q.strip()
        if q and 'Admin' in q and 'username' in q:
            user_query = q
            break
    
    if user_query:
        cursor.execute(user_query, (username, password))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Log the creation
    log_audit('CREATE', 'Admin', user_id, None, {
        'username': username
    })
    
    return user_id