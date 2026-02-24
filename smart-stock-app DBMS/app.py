import sqlite3
import json
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, redirect, session
from sql.sql_utils import load_sql_query

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

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

# Initialize database when app starts
init_db()

# Make session available in templates
@app.context_processor
def inject_session():
    return dict(session=session)

@app.route('/')
def home():
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    items_query = queries[0].strip()  # Get all items query
    items = conn.execute(items_query).fetchall()
    conn.close()
    return render_template('home.html', items=items)

@app.route('/sales', methods=['GET', 'POST'])
def sales():
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    
    if request.method == 'POST':
        date = request.form['date']
        item_code = request.form['item_code']
        
        # Load insert query from file
        queries = load_sql_query('insert_queries.sql').split(';')
        sales_query = None
        for query in queries:
            query = query.strip()
            if query and 'Sales' in query and 'date' in query:
                sales_query = query
                break
        
        if sales_query:
            conn.execute(sales_query, (date, item_code))
            conn.commit()
        conn.close()
        return redirect('/sales')
    
    # Get sales records
    queries = load_sql_query('read_queries.sql').split(';')
    sales_query = queries[4].strip()  # Get sales records query
    sales_records = conn.execute(sales_query).fetchall()
    
    # Get all items
    items_query = queries[0].strip()  # Get all items query
    items = conn.execute(items_query).fetchall()
    conn.close()
    
    return render_template('sales.html', sales_records=sales_records, items=items)

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
        
    if request.method == 'POST':
        location = request.form['location']
        item_code = request.form['item_code']
        qty = request.form['qty']
        
        # Load insert query from file
        queries = load_sql_query('insert_queries.sql').split(';')
        stock_query = None
        for query in queries:
            query = query.strip()
            if query and 'Stock' in query and 'location' in query:
                stock_query = query
                break
        
        if stock_query:
            conn.execute(stock_query, (location, item_code, qty))
            conn.commit()
        conn.close()
        return redirect('/stock')
    
    # Get stock records
    queries = load_sql_query('read_queries.sql').split(';')
    stock_query = queries[5].strip()  # Get stock records query
    stock_records = conn.execute(stock_query).fetchall()
    
    # Get all items
    items_query = queries[0].strip()  # Get all items query
    items = conn.execute(items_query).fetchall()
    conn.close()
    
    return render_template('stock.html', stock_records=stock_records, items=items)

@app.route('/transactions')
def transactions():
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    # Get all items
    queries = load_sql_query('read_queries.sql').split(';')
    items_query = queries[0].strip()  # Get all items query
    items = conn.execute(items_query).fetchall()
    
    items_with_transactions = []
    
    for item in items:
        # Get item transactions
        transaction_query = queries[3].strip()  # Get item transactions query
        transactions = conn.execute(transaction_query, (item['item_code'],)).fetchall()
        items_with_transactions.append({
            'item': item,
            'transactions': transactions
        })
    
    conn.close()
    return render_template('transactions.html', items_with_transactions=items_with_transactions)

@app.route('/add-item', methods=['GET', 'POST'])
def add_item():
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = None
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            name = request.form['name']
            qty = int(request.form['qty'])
            price = float(request.form['price'])
            
            # Check if an item with the same name already exists
            queries = load_sql_query('read_queries.sql').split(';')
            count_query = queries[10].strip()  # Check if item name exists query
            cursor = conn.execute(count_query, (name,))
            count = cursor.fetchone()[0]
            
            if count > 0:
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
                conn.execute(insert_query, (name, qty, price, 1))  # Default admin_id = 1
                conn.commit()
            return redirect('/')
    except ValueError as e:
        if conn:
            conn.close()
        return render_template('add_item.html', error=str(e))
    except Exception as e:
        if conn:
            conn.close()
        raise e
    
    if conn:
        conn.close()
    return render_template('add_item.html')

@app.route('/invoice/<int:item_id>')
def invoice(item_id):
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    item_query = queries[1].strip()  # Get specific item by ID query
    item = conn.execute(item_query, (item_id,)).fetchone()
    conn.close()
    return render_template('invoice.html', item=item)

@app.route('/edit-item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = None
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            name = request.form['name']
            qty = int(request.form['qty'])
            price = float(request.form['price'])
            
            # Check if another item with the same name already exists
            queries = load_sql_query('read_queries.sql').split(';')
            count_query = queries[11].strip()  # Check if another item with same name exists
            cursor = conn.execute(count_query, (name, item_id))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Get item for displaying in form
                item_query = queries[1].strip()  # Get specific item by ID query
                item = conn.execute(item_query, (item_id,)).fetchone()
                conn.close()
                raise ValueError(f"An item with the name '{name}' already exists.")
            
            # Load update query from file
            update_query = load_sql_query('update_queries.sql')
            conn.execute(update_query, (name, qty, price, item_id))
            conn.commit()
            conn.close()
            return redirect('/')
    except ValueError as e:
        # Get item for displaying in form
        if conn:
            conn.close()
        conn = get_db_connection()
        queries = load_sql_query('read_queries.sql').split(';')
        item_query = queries[1].strip()  # Get specific item by ID query
        item = conn.execute(item_query, (item_id,)).fetchone()
        conn.close()
        return render_template('edit_item.html', item=item, error=str(e))
    except Exception as e:
        if conn:
            conn.close()
        raise e
    
    # GET request
    queries = load_sql_query('read_queries.sql').split(';')
    item_query = queries[1].strip()  # Get specific item by ID query
    item = conn.execute(item_query, (item_id,)).fetchone()
    conn.close()
    return render_template('edit_item.html', item=item)

@app.route('/delete-item/<int:item_id>')
def delete_item_route(item_id):
    if 'logged_in' not in session:
        return redirect('/login')
        
    conn = get_db_connection()
    # Load delete query from file
    delete_query = load_sql_query('delete_queries.sql')
    conn.execute(delete_query, (item_id,))
    conn.commit()
    conn.close()
    return redirect('/')

# chart
@app.route('/stock-chart')
def stock_chart():
    conn = get_db_connection()
    # Load SQL query from file
    queries = load_sql_query('read_queries.sql').split(';')
    chart_query = queries[12].strip()  # Get chart query (corrected index)
    data = conn.execute(chart_query).fetchall()
    conn.close()

    # Handle case when no items exist
    if not data:
        # Create a chart with a message
        plt.figure(figsize=(5, 2.5))  # Even smaller size
        plt.text(0.5, 0.5, 'No items in inventory', horizontalalignment='center', 
                verticalalignment='center', transform=plt.gca().transAxes, 
                fontsize=12, fontweight='bold')  # Smaller font
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.axis('off')
        plt.title('Current Stock Levels by Item', fontsize=10, fontweight='bold', pad=8)  # Smaller font
    else:
        # Check if we have data with the expected structure
        try:
            items = [row[0] for row in data]
            quantities = [row[1] for row in data]
        except (IndexError, TypeError):
            # If there's an issue with data structure, show no items message
            plt.figure(figsize=(5, 2.5))
            plt.text(0.5, 0.5, 'No items in inventory', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes, 
                    fontsize=12, fontweight='bold')
            plt.xlim(0, 1)
            plt.ylim(0, 1)
            plt.axis('off')
            plt.title('Current Stock Levels by Item', fontsize=10, fontweight='bold', pad=8)
        else:
            # Only create chart if we have valid data
            if items and quantities:
                # Create an enhanced bar chart with smaller size
                plt.figure(figsize=(6, 3))  # Smaller size from (8, 4) to (6, 3)
                bars = plt.bar(items, quantities, color='#3498db', edgecolor='#2c3e50', linewidth=0.3)
                
                # Add value labels on bars with smaller font
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    plt.text(bar.get_x() + bar.get_width()/2, height + max(quantities)*0.01, str(quantities[i]),
                            ha='center', va='bottom', fontsize=7, fontweight='bold', color='#2c3e50')  # Smaller font
                
                # Improve chart appearance with smaller fonts
                plt.title('Current Stock Levels by Item', fontsize=12, fontweight='bold', pad=12)  # Smaller font
                plt.xlabel('Item Name', fontsize=8, fontweight='bold')  # Smaller font
                plt.ylabel('Quantity in Stock', fontsize=8, fontweight='bold')  # Smaller font
                
                # Add grid for better readability
                plt.grid(axis='y', alpha=0.3)
                
                # Rotate x-axis labels if there are many items
                if len(items) > 5:
                    plt.xticks(rotation=45, ha='right', fontsize=7)  # Smaller font
                else:
                    plt.xticks(fontsize=7)  # Smaller font
                    
                plt.yticks(fontsize=7)  # Smaller font
                
                # Add some styling
                plt.gca().spines['top'].set_visible(False)
                plt.gca().spines['right'].set_visible(False)
            else:
                # Create a chart with a message if no valid data
                plt.figure(figsize=(5, 2.5))
                plt.text(0.5, 0.5, 'No items in inventory', horizontalalignment='center', 
                        verticalalignment='center', transform=plt.gca().transAxes, 
                        fontsize=12, fontweight='bold')
                plt.xlim(0, 1)
                plt.ylim(0, 1)
                plt.axis('off')
                plt.title('Current Stock Levels by Item', fontsize=10, fontweight='bold', pad=8)
        
    # Adjust layout and save with same quality
    plt.tight_layout()
    plt.savefig('static/stock_chart.png', dpi=300, bbox_inches='tight')
    plt.close()

    return render_template('stock-chart.html')

@app.route('/audit-trail')
def audit_trail():
    conn = get_db_connection()
    queries = load_sql_query('read_queries.sql').split(';')
    audit_query = queries[2].strip()  # Get audit trail query
    audit_entries = conn.execute(audit_query).fetchall()
    conn.close()
    return render_template('audit_trail.html', audit_entries=audit_entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        queries = load_sql_query('read_queries.sql').split(';')
        verify_query = queries[7].strip()  # Verify user query
        user = conn.execute(verify_query, (username, password)).fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match')
        
        conn = None
        try:
            conn = get_db_connection()
            # Check if username already exists
            queries = load_sql_query('read_queries.sql').split(';')
            count_query = queries[9].strip()  # Check if username exists query
            cursor = conn.execute(count_query, (username,))
            count = cursor.fetchone()[0]
            
            if count > 0:
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
                conn.execute(user_query, (username, password))
                conn.commit()
            return redirect('/login')
        except ValueError as e:
            if conn:
                conn.close()
            return render_template('register.html', error=str(e))
        except Exception as e:
            if conn:
                conn.close()
            raise e
    
    if conn:
        conn.close()
    return render_template('register.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    conn = get_db_connection()
    if query:
        queries = load_sql_query('read_queries.sql').split(';')
        search_query = queries[6].strip()  # Search items query
        items = conn.execute(search_query, (f'%{query}%', f'%{query}%')).fetchall()
        conn.close()
        return render_template('home.html', items=items, search_query=query)
    else:
        queries = load_sql_query('read_queries.sql').split(';')
        items_query = queries[0].strip()  # Get all items query
        items = conn.execute(items_query).fetchall()
        conn.close()
        return render_template('home.html', items=items)

if __name__ == '__main__':
    app.run(debug=True)