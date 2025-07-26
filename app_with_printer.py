from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import os

# Drucker Support importieren
try:
    from printer_support import EpsonTMT88VPrinter, add_printer_routes
    PRINTER_AVAILABLE = True
except ImportError:
    PRINTER_AVAILABLE = False
    print("⚠️  Drucker-Support nicht verfügbar. Installieren Sie pywin32 für Windows-Druckfunktionen.")

app = Flask(__name__)
CORS(app)

# Database initialization (same as original)
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
            cashier TEXT DEFAULT 'System',
            printed BOOLEAN DEFAULT 0
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

# Routes (same as original app.py)
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

# Enhanced Sales management with printer support
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
        
        # Automatisches Drucken wenn Drucker verfügbar
        print_result = None
        if PRINTER_AVAILABLE and data.get('auto_print', True):
            print_result = print_sale_receipt(sale_id)
            if print_result and print_result.get('success'):
                cursor.execute('UPDATE sales SET printed = 1 WHERE id = ?', (sale_id,))
                conn.commit()
        
        conn.close()
        
        result = {'success': True, 'sale_id': sale_id}
        if print_result:
            result['print_result'] = print_result
            
        return jsonify(result)
        
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
            'printed': bool(row[5]) if len(row) > 5 else False,
            'item_count': row[-1]
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
    
    if not sale_row:
        conn.close()
        return jsonify({'error': 'Verkauf nicht gefunden'}), 404
    
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
        'printed': bool(sale_row[5]) if len(sale_row) > 5 else False,
        'items': items
    }
    
    conn.close()
    return jsonify(sale)

# Printer-specific routes
def print_sale_receipt(sale_id):
    """Helper function to print a receipt for a sale"""
    if not PRINTER_AVAILABLE:
        return {'success': False, 'error': 'Drucker nicht verfügbar'}
    
    # Get sale data
    conn = sqlite3.connect('kassensystem.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sales WHERE id=?', (sale_id,))
    sale_row = cursor.fetchone()
    
    if not sale_row:
        conn.close()
        return {'success': False, 'error': 'Verkauf nicht gefunden'}
    
    cursor.execute('''
        SELECT si.*, p.name
        FROM sale_items si
        JOIN products p ON si.product_id = p.id
        WHERE si.sale_id = ?
    ''', (sale_id,))
    
    items = []
    for row in cursor.fetchall():
        items.append({
            'name': row[6],
            'quantity': row[3],
            'unit_price': row[4],
            'total_price': row[5]
        })
    
    conn.close()
    
    # Prepare sale data for printer
    sale_data = {
        'sale_id': sale_row[0],
        'total_amount': sale_row[1],
        'payment_method': sale_row[2],
        'created_at': sale_row[3],
        'cashier': sale_row[4],
        'items': items
    }
    
    # Print receipt
    try:
        printer = EpsonTMT88VPrinter()
        result = printer.print_receipt(sale_data)
        return result
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/api/sales/<int:sale_id>/print', methods=['POST'])
def reprint_receipt(sale_id):
    """Manually reprint a receipt"""
    result = print_sale_receipt(sale_id)
    
    # Update printed status if successful
    if result.get('success'):
        conn = sqlite3.connect('kassensystem.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE sales SET printed = 1 WHERE id = ?', (sale_id,))
        conn.commit()
        conn.close()
    
    return jsonify(result)

# Reports (same as original)
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

# System info
@app.route('/api/system/info')
def system_info():
    info = {
        'printer_available': PRINTER_AVAILABLE,
        'version': '2.0',
        'features': [
            'Produktverwaltung',
            'Verkaufsabwicklung',
            'Berichtswesen',
            'Belegdruck' if PRINTER_AVAILABLE else 'Kein Drucker'
        ]
    }
    
    if PRINTER_AVAILABLE:
        try:
            printer = EpsonTMT88VPrinter()
            printers = printer.list_printers()
            epson_printer = printer.find_epson_printer()
            
            info['printers'] = {
                'available': printers,
                'epson_found': epson_printer,
                'current': printer.printer_name
            }
        except Exception as e:
            info['printer_error'] = str(e)
    
    return jsonify(info)

# Add printer routes if available
if PRINTER_AVAILABLE:
    add_printer_routes(app)

if __name__ == '__main__':
    init_db()
    
    print("🚀 Kassensystem mit Druckfunktion startet...")
    print("💻 Webinterface: http://localhost:5000")
    
    if PRINTER_AVAILABLE:
        print("🖨️  Drucker-Support: Aktiviert")
        try:
            printer = EpsonTMT88VPrinter()
            print(f"🖨️  Aktueller Drucker: {printer.printer_name}")
            
            epson = printer.find_epson_printer()
            if epson:
                print(f"🖨️  Epson TMT88V gefunden: {epson}")
            else:
                print("⚠️  Kein Epson TMT88V Drucker gefunden")
                
        except Exception as e:
            print(f"⚠️  Drucker-Initialisierung fehlgeschlagen: {e}")
    else:
        print("❌ Drucker-Support: Nicht verfügbar")
        print("   Installieren Sie pywin32: pip install pywin32")
    
    print("")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)