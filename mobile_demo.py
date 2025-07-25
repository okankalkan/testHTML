from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Mobile-optimized HTML template
MOBILE_TEMPLATE = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>📱 Mobile Kassensystem</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 10px;
            color: #333;
        }
        
        .app {
            max-width: 400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .header h1 {
            color: #4CAF50;
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        
        .time {
            font-size: 1.1rem;
            color: #666;
            font-weight: 500;
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .products-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .product-btn {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px 10px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 5px;
            min-height: 80px;
            justify-content: center;
        }
        
        .product-btn:active {
            transform: scale(0.95);
            box-shadow: 0 2px 10px rgba(76, 175, 80, 0.3);
        }
        
        .price {
            font-weight: bold;
            font-size: 0.8rem;
        }
        
        .barcode-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            font-size: 1.1rem;
            margin-bottom: 10px;
        }
        
        .barcode-input:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        .add-btn {
            width: 100%;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .add-btn:active {
            background: #45a049;
            transform: scale(0.98);
        }
        
        .cart {
            background: #f8f9fa;
            border-radius: 15px;
            padding: 15px;
            min-height: 120px;
        }
        
        .cart-empty {
            text-align: center;
            color: #999;
            padding: 30px 0;
        }
        
        .cart-item {
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        .cart-item-info {
            flex: 1;
        }
        
        .cart-item-name {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .cart-item-details {
            font-size: 0.9rem;
            color: #666;
        }
        
        .cart-controls {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .qty-btn {
            background: #f0f0f0;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        
        .qty-btn:active {
            background: #e0e0e0;
        }
        
        .qty-display {
            font-weight: 600;
            min-width: 30px;
            text-align: center;
        }
        
        .remove-btn {
            background: #f44336;
            color: white;
            border: none;
            border-radius: 50%;
            width: 35px;
            height: 35px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .total {
            background: #4CAF50;
            color: white;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.3rem;
            font-weight: bold;
        }
        
        .payment-methods {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .payment-btn {
            flex: 1;
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 15px;
            padding: 15px 10px;
            cursor: pointer;
            text-align: center;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }
        
        .payment-btn.active {
            border-color: #4CAF50;
            background: rgba(76, 175, 80, 0.1);
            color: #4CAF50;
        }
        
        .complete-btn {
            width: 100%;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 20px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .complete-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        
        .complete-btn:not(:disabled):active {
            background: #45a049;
            transform: scale(0.98);
        }
        
        .clear-btn {
            width: 100%;
            background: #f44336;
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px;
            font-size: 1.1rem;
            cursor: pointer;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }
        
        .clear-btn:active {
            background: #d32f2f;
            transform: scale(0.98);
        }
        
        .notification {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #4CAF50;
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            animation: slideDown 0.3s ease;
        }
        
        .notification.error {
            background: #f44336;
        }
        
        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateX(-50%) translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        }
        
        .demo-badge {
            position: fixed;
            top: 10px;
            right: 10px;
            background: rgba(255, 193, 7, 0.9);
            color: #333;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: bold;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div class="demo-badge">📱 MOBILE DEMO</div>
    
    <div class="app">
        <div class="header">
            <h1><i class="fas fa-cash-register"></i> Kassensystem</h1>
            <div class="time" id="currentTime"></div>
        </div>
        
        <!-- Produktsuche -->
        <div class="section">
            <h3><i class="fas fa-search"></i> Produktsuche</h3>
            <input type="text" class="barcode-input" id="barcodeInput" placeholder="Barcode eingeben" autocomplete="off">
            <button class="add-btn" onclick="searchProduct()">
                <i class="fas fa-plus"></i> Hinzufügen
            </button>
        </div>
        
        <!-- Schnellzugriff -->
        <div class="section">
            <h3><i class="fas fa-bolt"></i> Schnellzugriff</h3>
            <div class="products-grid" id="quickProducts">
                <!-- Wird von JavaScript gefüllt -->
            </div>
        </div>
        
        <!-- Warenkorb -->
        <div class="section">
            <h3><i class="fas fa-shopping-cart"></i> Warenkorb</h3>
            <div class="cart" id="cartItems">
                <div class="cart-empty">
                    <i class="fas fa-shopping-cart" style="font-size: 2rem; opacity: 0.5; margin-bottom: 10px;"></i>
                    <div>Warenkorb ist leer</div>
                </div>
            </div>
            
            <div class="total" id="totalAmount">0,00 €</div>
            
            <!-- Zahlungsarten -->
            <div class="payment-methods">
                <button class="payment-btn active" data-method="Bargeld">
                    <i class="fas fa-money-bills"></i><br>Bargeld
                </button>
                <button class="payment-btn" data-method="Karte">
                    <i class="fas fa-credit-card"></i><br>Karte
                </button>
                <button class="payment-btn" data-method="Kontaktlos">
                    <i class="fas fa-wifi"></i><br>NFC
                </button>
            </div>
            
            <button class="clear-btn" onclick="clearCart()">
                <i class="fas fa-trash"></i> Warenkorb leeren
            </button>
            
            <button class="complete-btn" onclick="completeSale()" id="completeSaleBtn" disabled>
                <i class="fas fa-check"></i> Verkauf abschließen
            </button>
        </div>
    </div>

    <script>
        // Global variables
        let cart = [];
        let products = [];
        let currentPaymentMethod = 'Bargeld';

        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            loadProducts();
            updateTime();
            setupEventListeners();
            setInterval(updateTime, 1000);
        });

        // Update current time
        function updateTime() {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleTimeString('de-DE');
        }

        // Setup event listeners
        function setupEventListeners() {
            document.getElementById('barcodeInput').addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchProduct();
                }
            });
            
            document.querySelectorAll('.payment-btn').forEach(btn => {
                btn.addEventListener('click', function() {
                    selectPaymentMethod(this.dataset.method);
                });
            });
        }

        // Load products
        async function loadProducts() {
            try {
                const response = await fetch('/api/products');
                const data = await response.json();
                products = data;
                displayQuickProducts();
            } catch (error) {
                console.error('Error loading products:', error);
                showNotification('Demo-Modus: Beispielprodukte werden geladen', 'info');
                // Fallback demo products
                products = [
                    {id: 1, name: 'Apfel', price: 0.50, barcode: '1111'},
                    {id: 2, name: 'Banane', price: 0.30, barcode: '2222'},
                    {id: 3, name: 'Brot', price: 2.50, barcode: '3333'},
                    {id: 4, name: 'Milch', price: 1.20, barcode: '4444'},
                    {id: 5, name: 'Cola', price: 1.50, barcode: '5555'},
                    {id: 6, name: 'Chips', price: 1.99, barcode: '6666'}
                ];
                displayQuickProducts();
            }
        }

        // Display quick products
        function displayQuickProducts() {
            const container = document.getElementById('quickProducts');
            container.innerHTML = products.slice(0, 6).map(product => 
                `<button class="product-btn" onclick="addToCart(${product.id})">
                    <div>${product.name}</div>
                    <div class="price">${formatPrice(product.price)}</div>
                </button>`
            ).join('');
        }

        // Search product
        function searchProduct() {
            const barcode = document.getElementById('barcodeInput').value.trim();
            if (!barcode) return;
            
            const product = products.find(p => p.barcode === barcode);
            if (product) {
                addToCart(product.id);
                document.getElementById('barcodeInput').value = '';
            } else {
                showNotification('Produkt nicht gefunden', 'error');
            }
        }

        // Add to cart
        function addToCart(productId) {
            const product = products.find(p => p.id === productId);
            if (!product) return;
            
            const existingItem = cart.find(item => item.product_id === productId);
            
            if (existingItem) {
                existingItem.quantity++;
                existingItem.total_price = existingItem.quantity * existingItem.unit_price;
            } else {
                cart.push({
                    product_id: productId,
                    name: product.name,
                    unit_price: product.price,
                    quantity: 1,
                    total_price: product.price
                });
            }
            
            updateCartDisplay();
            showNotification(`${product.name} hinzugefügt`);
        }

        // Update cart display
        function updateCartDisplay() {
            const container = document.getElementById('cartItems');
            
            if (cart.length === 0) {
                container.innerHTML = `
                    <div class="cart-empty">
                        <i class="fas fa-shopping-cart" style="font-size: 2rem; opacity: 0.5; margin-bottom: 10px;"></i>
                        <div>Warenkorb ist leer</div>
                    </div>
                `;
            } else {
                container.innerHTML = cart.map((item, index) => `
                    <div class="cart-item">
                        <div class="cart-item-info">
                            <div class="cart-item-name">${item.name}</div>
                            <div class="cart-item-details">${formatPrice(item.unit_price)} × ${item.quantity}</div>
                        </div>
                        <div class="cart-controls">
                            <button class="qty-btn" onclick="updateQuantity(${index}, -1)">-</button>
                            <span class="qty-display">${item.quantity}</span>
                            <button class="qty-btn" onclick="updateQuantity(${index}, 1)">+</button>
                            <button class="remove-btn" onclick="removeFromCart(${index})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                `).join('');
            }
            
            updateCartTotal();
        }

        // Update quantity
        function updateQuantity(index, change) {
            const item = cart[index];
            const newQuantity = item.quantity + change;
            
            if (newQuantity <= 0) {
                removeFromCart(index);
                return;
            }
            
            item.quantity = newQuantity;
            item.total_price = item.quantity * item.unit_price;
            updateCartDisplay();
        }

        // Remove from cart
        function removeFromCart(index) {
            cart.splice(index, 1);
            updateCartDisplay();
        }

        // Clear cart
        function clearCart() {
            if (cart.length === 0) return;
            cart = [];
            updateCartDisplay();
            showNotification('Warenkorb geleert');
        }

        // Update cart total
        function updateCartTotal() {
            const total = cart.reduce((sum, item) => sum + item.total_price, 0);
            document.getElementById('totalAmount').textContent = formatPrice(total);
            updateCompleteSaleButton();
        }

        // Select payment method
        function selectPaymentMethod(method) {
            currentPaymentMethod = method;
            document.querySelectorAll('.payment-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-method="${method}"]`).classList.add('active');
            updateCompleteSaleButton();
        }

        // Update complete sale button
        function updateCompleteSaleButton() {
            const btn = document.getElementById('completeSaleBtn');
            btn.disabled = cart.length === 0;
        }

        // Complete sale
        async function completeSale() {
            if (cart.length === 0) return;
            
            const total = cart.reduce((sum, item) => sum + item.total_price, 0);
            
            showNotification(`Verkauf abgeschlossen! Gesamt: ${formatPrice(total)} (${currentPaymentMethod})`, 'success');
            
            // In demo mode, just clear cart
            setTimeout(() => {
                clearCart();
                selectPaymentMethod('Bargeld');
            }, 1500);
        }

        // Format price
        function formatPrice(price) {
            return new Intl.NumberFormat('de-DE', {
                style: 'currency',
                currency: 'EUR'
            }).format(price);
        }

        // Show notification
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            notification.textContent = message;
            document.body.appendChild(notification);
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 3000);
        }
    </script>
</body>
</html>
"""

# Database setup (same as main app)
def init_db():
    conn = sqlite3.connect('mobile_kassensystem.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            barcode TEXT UNIQUE,
            stock INTEGER DEFAULT 0
        )
    ''')
    
    # Sample products
    cursor.execute('SELECT COUNT(*) FROM products')
    if cursor.fetchone()[0] == 0:
        sample_products = [
            ('Apfel', 0.50, 'Obst', '1111', 100),
            ('Banane', 0.30, 'Obst', '2222', 80),
            ('Brot', 2.50, 'Backwaren', '3333', 20),
            ('Milch', 1.20, 'Molkereiprodukte', '4444', 30),
            ('Cola', 1.50, 'Getränke', '5555', 50),
            ('Chips', 1.99, 'Snacks', '6666', 40)
        ]
        cursor.executemany(
            'INSERT INTO products (name, price, category, barcode, stock) VALUES (?, ?, ?, ?, ?)',
            sample_products
        )
    
    conn.commit()
    conn.close()

@app.route('/')
def mobile_app():
    return render_template_string(MOBILE_TEMPLATE)

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = sqlite3.connect('mobile_kassensystem.db')
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
            'stock': row[5]
        })
    conn.close()
    return jsonify(products)

if __name__ == '__main__':
    init_db()
    print("📱 Mobile Kassensystem startet...")
    print("🌐 Für iPhone/Mobile optimiert!")
    print("📲 Zugriff über: http://0.0.0.0:8080")
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=True)