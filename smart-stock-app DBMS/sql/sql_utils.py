import os

def load_sql_query(filename):
    """Load SQL query from file"""
    sql_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(sql_dir, filename)
    
    with open(file_path, 'r') as file:
        return file.read().strip()