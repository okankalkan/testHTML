from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            barcode TEXT UNIQUE,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_amount REAL NOT NULL,
            payment_method TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cashier TEXT DEFAULT 'System'
        )
    ''')
    
    # Sale items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            product_id INTEGER,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            total_price REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert sample products if table is empty
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Apfel', 0.50, 'Obst', '1234567890123', 100),
            ('Banane', 0.30, 'Obst', '1234567890124', 80),
            ('Brot', 2.50, 'Backwaren', '1234567890125', 20),
            ('Milch', 1.20, 'Molkereiprodukte', '1234567890126', 30),
            ('Kaffee', 4.99, 'Getränke', '1234567890127', 15),
            ('Cola', 1.50, 'Getränke', '1234567890128', 50),
            ('Schokolade', 2.99, 'Süßwaren', '1234567890129', 25),
            ('Chips', 1.99, 'Snacks', '1234567890130', 40)
        ]
        cursor.executemany(
            'INSERT INTO products (name, price, category, barcode, stock) VALUES (?, ?, ?, ?, ?)',
            sample_products
        )
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Product management
@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products ORDER BY name')
    products = []
    for row in cursor.fetchall():
        products.append({
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'category': row[3],
            'barcode': row[4],
            'stock': row[5],
            'created_at': row[6]
        })
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO products (name, price, category, barcode, stock) VALUES (?, ?, ?, ?, ?)',
            (data['name'], data['price'], data.get('category', ''), data.get('barcode', ''), data.get('stock', 0))
        )
        conn.commit()
        product_id = cursor.lastrowid
        conn.close()
        return jsonify({'success': True, 'id': product_id})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Barcode bereits vorhanden'})

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE products SET name=?, price=?, category=?, barcode=?, stock=? WHERE id=?',
        (data['name'], data['price'], data.get('category', ''), data.get('barcode', ''), data.get('stock', 0), product_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/products/search/<barcode>')
def search_product_by_barcode(barcode):
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE barcode=?', (barcode,))
    row = cursor.fetchone()
    if row:
        product = {
            'id': row[0],
            'name': row[1],
            'price': row[2],
            'category': row[3],
            'barcode': row[4],
            'stock': row[5]
        }
        conn.close()
        return jsonify({'success': True, 'product': product})
    else:
        conn.close()
        return jsonify({'success': False, 'error': 'Produkt nicht gefunden'})

# Sales management
@app.route('/api/sales', methods=['POST'])
def create_sale():
    data = request.json
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    
    try:
        # Create sale record
        cursor.execute(
            'INSERT INTO sales (total_amount, payment_method, cashier) VALUES (?, ?, ?)',
            (data['total_amount'], data['payment_method'], data.get('cashier', 'System'))
        )
        sale_id = cursor.lastrowid
        
        # Add sale items and update stock
        for item in data['items']:
            cursor.execute(
                'INSERT INTO sale_items (sale_id, product_id, quantity, unit_price, total_price) VALUES (?, ?, ?, ?, ?)',
                (sale_id, item['product_id'], item['quantity'], item['unit_price'], item['total_price'])
            )
            # Update stock
            cursor.execute(
                'UPDATE products SET stock = stock - ? WHERE id = ?',
                (item['quantity'], item['product_id'])
            )
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'sale_id': sale_id})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/sales', methods=['GET'])
def get_sales():
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, COUNT(si.id) as item_count
        FROM sales s
        LEFT JOIN sale_items si ON s.id = si.sale_id
        GROUP BY s.id
        ORDER BY s.created_at DESC
        LIMIT 100
    ''')
    sales = []
    for row in cursor.fetchall():
        sales.append({
            'id': row[0],
            'total_amount': row[1],
            'payment_method': row[2],
            'created_at': row[3],
            'cashier': row[4],
            'item_count': row[5]
        })
    conn.close()
    return jsonify(sales)

@app.route('/api/sales/<int:sale_id>')
def get_sale_details(sale_id):
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    
    # Get sale info
    cursor.execute('SELECT * FROM sales WHERE id=?', (sale_id,))
    sale_row = cursor.fetchone()
    
    # Get sale items
    cursor.execute('''
        SELECT si.*, p.name, p.category
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
    ''', (sale_id,))
    items = []
    for row in cursor.fetchall():
        items.append({
            'id': row[0],
            'product_id': row[2],
            'quantity': row[3],
            'unit_price': row[4],
            'total_price': row[5],
            'product_name': row[6],
            'category': row[7]
        })
    
    sale = {
        'id': sale_row[0],
        'total_amount': sale_row[1],
        'payment_method': sale_row[2],
        'created_at': sale_row[3],
        'cashier': sale_row[4],
        'items': items
    }
    
    conn.close()
    return jsonify(sale)

# Reports
@app.route('/api/reports/daily')
def daily_report():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    
    # Daily sales summary
    cursor.execute('''
        SELECT 
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_revenue,
            AVG(total_amount) as avg_transaction,
            payment_method,
            COUNT(*) as payment_count
        FROM sales 
        WHERE DATE(created_at) = ?
        GROUP BY payment_method
    ''', (date,))
    
    payment_summary = []
    total_revenue = 0
    total_transactions = 0
    
    for row in cursor.fetchall():
        payment_summary.append({
            'payment_method': row[3],
            'count': row[4],
            'amount': row[1] if row[1] else 0
        })
        if row[1]:
            total_revenue += row[1]
        total_transactions += row[0]
    
    # Top selling products
    cursor.execute('''
        SELECT 
            p.name,
            SUM(si.quantity) as total_quantity,
            SUM(si.total_price) as total_revenue
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        JOIN sales s ON si.sale_id = s.id
        WHERE DATE(s.created_at) = ?
        GROUP BY p.id, p.name
        ORDER BY total_quantity DESC
        LIMIT 10
    ''', (date,))
    
    top_products = []
    for row in cursor.fetchall():
        top_products.append({
            'name': row[0],
            'quantity': row[1],
            'revenue': row[2]
        })
    
    conn.close()
    
    return jsonify({
        'date': date,
        'total_revenue': total_revenue,
        'total_transactions': total_transactions,
        'avg_transaction': total_revenue / total_transactions if total_transactions > 0 else 0,
        'payment_summary': payment_summary,
        'top_products': top_products
    })

if __name__ == '__main__':
    init_db()
    print("🚀 Kassensystem startet...")
    print("📱 Zugriff über: http://0.0.0.0:5000")
    print("💻 Lokal: http://localhost:5000")
    print("🌐 Remote: http://<your-ip>:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)