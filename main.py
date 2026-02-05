from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)

# Get database path from environment variable or use default
DATABASE_PATH = os.getenv('DATABASE_PATH', 'ecommerce.db')

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  email TEXT,
                  password TEXT,
                  created_at TEXT)''')
    
    # Products table
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  price REAL NOT NULL,
                  stock INTEGER NOT NULL,
                  description TEXT)''')
    
    # Cart table
    c.execute('''CREATE TABLE IF NOT EXISTS cart
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  product_ids TEXT,
                  created_at TEXT,
                  updated_at TEXT)''')
    
    # Orders table
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  cart_id INTEGER,
                  total REAL,
                  status TEXT,
                  created_at TEXT)''')
    
    # Insert sample products
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        products = [
            ("Laptop", 999.99, 10, "High performance laptop"),
            ("Mouse", 29.99, 50, "Wireless mouse"),
            ("Keyboard", 79.99, 30, "Mechanical keyboard"),
            ("Monitor", 299.99, 15, "27 inch 4K monitor"),
            ("Headphones", 149.99, 25, "Noise cancelling headphones")
        ]
        c.executemany("INSERT INTO products (name, price, stock, description) VALUES (?, ?, ?, ?)", products)
    
    conn.commit()
    conn.close()

# BUG: No input validation on email
# BUG: No unique check on username
# BUG: Password stored in plain text
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    # BUG: SQL Injection vulnerability - using string concatenation
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    query = f"INSERT INTO users (username, email, password, created_at) VALUES ('{username}', '{email}', '{password}', '{datetime.now()}')"
    
    try:
        c.execute(query)
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        return jsonify({
            "message": "User created successfully",
            "user_id": user_id
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 400

# BUG: Returns all sensitive data including passwords
# BUG: SQL Injection in query parameters
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # BUG: SQL Injection via query parameters
    user_id = request.args.get('id', '')
    if user_id:
        query = f"SELECT * FROM users WHERE id = {user_id}"
    else:
        query = "SELECT * FROM users"
    
    c.execute(query)
    users = c.fetchall()
    conn.close()
    
    # BUG: Returning sensitive data (passwords)
    user_list = []
    for user in users:
        user_list.append({
            "id": user[0],
            "username": user[1],
            "email": user[2],
            "password": user[3],  # BUG: Exposing passwords
            "created_at": user[4]
        })
    
    return jsonify({"users": user_list}), 200

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # BUG: SQL Injection via search parameter
    search = request.args.get('search', '')
    if search:
        query = f"SELECT * FROM products WHERE name LIKE '%{search}%'"
        c.execute(query)
    else:
        c.execute("SELECT * FROM products")
    
    products = c.fetchall()
    conn.close()
    
    product_list = []
    for product in products:
        product_list.append({
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "stock": product[3],
            "description": product[4]
        })
    
    return jsonify({"products": product_list}), 200

# BUG: Any user can manipulate any cart by providing any user_id
# BUG: No validation that products exist
# BUG: No stock checking
@app.route('/api/cart', methods=['POST'])
def create_update_cart():
    data = request.get_json()
    
    user_id = data.get('user_id')
    product_ids = data.get('product_ids', [])
    
    # BUG: No authentication - anyone can modify anyone's cart
    # BUG: No validation that user exists
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # Check if cart exists for user
    c.execute(f"SELECT * FROM cart WHERE user_id = {user_id}")
    existing_cart = c.fetchone()
    
    product_ids_str = json.dumps(product_ids)
    
    if existing_cart:
        # Update existing cart
        query = f"UPDATE cart SET product_ids = '{product_ids_str}', updated_at = '{datetime.now()}' WHERE user_id = {user_id}"
        c.execute(query)
        cart_id = existing_cart[0]
    else:
        # Create new cart
        query = f"INSERT INTO cart (user_id, product_ids, created_at, updated_at) VALUES ({user_id}, '{product_ids_str}', '{datetime.now()}', '{datetime.now()}')"
        c.execute(query)
        cart_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Cart updated successfully",
        "cart_id": cart_id,
        "user_id": user_id,
        "product_ids": product_ids
    }), 200

# BUG: No validation on user_id or product_id
@app.route('/api/cart/<int:cart_id>/remove', methods=['POST'])
def remove_from_cart(cart_id):
    data = request.get_json()
    product_id = data.get('product_id')
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    c.execute(f"SELECT product_ids FROM cart WHERE id = {cart_id}")
    cart = c.fetchone()
    
    if not cart:
        conn.close()
        return jsonify({"error": "Cart not found"}), 404
    
    product_ids = json.loads(cart[0])
    
    # BUG: No error handling if product_id not in cart
    product_ids.remove(product_id)
    
    product_ids_str = json.dumps(product_ids)
    query = f"UPDATE cart SET product_ids = '{product_ids_str}', updated_at = '{datetime.now()}' WHERE id = {cart_id}"
    c.execute(query)
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Product removed from cart",
        "cart_id": cart_id,
        "product_ids": product_ids
    }), 200

# BUG: Accepts any user_id or cart_id without validation
# BUG: No authentication check
# BUG: Doesn't verify cart belongs to user
# BUG: Doesn't check stock availability
# BUG: Doesn't update stock after checkout
@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    
    user_id = data.get('user_id')
    cart_id = data.get('cart_id')
    
    # BUG: No validation that user or cart exists
    # BUG: No validation that cart belongs to user
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # BUG: SQL Injection vulnerability
    c.execute(f"SELECT product_ids FROM cart WHERE id = {cart_id}")
    cart = c.fetchone()
    
    if not cart:
        conn.close()
        return jsonify({"error": "Cart not found"}), 404
    
    product_ids = json.loads(cart[0])
    
    # Calculate total (BUG: no stock check)
    total = 0
    for pid in product_ids:
        c.execute(f"SELECT price FROM products WHERE id = {pid}")
        product = c.fetchone()
        if product:
            total += product[0]
    
    # BUG: Doesn't reduce stock after purchase
    # Create order
    query = f"INSERT INTO orders (user_id, cart_id, total, status, created_at) VALUES ({user_id}, {cart_id}, {total}, 'completed', '{datetime.now()}')"
    c.execute(query)
    order_id = c.lastrowid
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Checkout successful",
        "order_id": order_id,
        "total": total,
        "user_id": user_id
    }), 200

# BUG: Exposes order information without authentication
@app.route('/api/orders', methods=['GET'])
def get_orders():
    user_id = request.args.get('user_id', '')
    
    conn = sqlite3.connect(DATABASE_PATH)
    c = conn.cursor()
    
    # BUG: SQL Injection
    if user_id:
        query = f"SELECT * FROM orders WHERE user_id = {user_id}"
    else:
        query = "SELECT * FROM orders"
    
    c.execute(query)
    orders = c.fetchall()
    conn.close()
    
    order_list = []
    for order in orders:
        order_list.append({
            "id": order[0],
            "user_id": order[1],
            "cart_id": order[2],
            "total": order[3],
            "status": order[4],
            "created_at": order[5]
        })
    
    return jsonify({"orders": order_list}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
