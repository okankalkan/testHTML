// Global variables
let cart = [];
let products = [];
let currentPaymentMethod = 'Bargeld';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    loadRecentSales();
    updateTime();
    setupEventListeners();
    
    // Update time every second
    setInterval(updateTime, 1000);
});

// Update current time display
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('de-DE');
    document.getElementById('currentTime').textContent = timeString;
}

// Setup event listeners
function setupEventListeners() {
    // Barcode input enter key
    document.getElementById('barcodeInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchProduct();
        }
    });
    
    // Payment method buttons
    document.querySelectorAll('.payment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            selectPaymentMethod(this.dataset.method);
        });
    });
    
    // Received amount calculation
    document.getElementById('receivedAmount').addEventListener('input', calculateChange);
    
    // Product form submission
    document.getElementById('productForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addNewProduct();
    });
    
    // Modal close on outside click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                this.style.display = 'none';
            }
        });
    });
}

// Load products from server
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const data = await response.json();
        products = data;
        displayQuickProducts();
        updateProductTable();
    } catch (error) {
        console.error('Error loading products:', error);
        showNotification('Fehler beim Laden der Produkte', 'error');
    }
}

// Display quick access products
function displayQuickProducts() {
    const container = document.getElementById('quickProducts');
    const quickProducts = products.slice(0, 8); // Show first 8 products
    
    container.innerHTML = quickProducts.map(product => `
        <button class="product-quick-btn" onclick="addToCart(${product.id})">
            <div>${product.name}</div>
            <div class="price">${formatPrice(product.price)}</div>
        </button>
    `).join('');
}

// Search product by barcode
async function searchProduct() {
    const barcode = document.getElementById('barcodeInput').value.trim();
    if (!barcode) return;
    
    try {
        const response = await fetch(`/api/products/search/${barcode}`);
        const data = await response.json();
        
        if (data.success) {
            addToCart(data.product.id);
            document.getElementById('barcodeInput').value = '';
        } else {
            showNotification('Produkt nicht gefunden', 'error');
        }
    } catch (error) {
        console.error('Error searching product:', error);
        showNotification('Fehler bei der Produktsuche', 'error');
    }
}

// Add product to cart
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    if (product.stock <= 0) {
        showNotification('Produkt nicht auf Lager', 'error');
        return;
    }
    
    const existingItem = cart.find(item => item.product_id === productId);
    
    if (existingItem) {
        if (existingItem.quantity < product.stock) {
            existingItem.quantity++;
            existingItem.total_price = existingItem.quantity * existingItem.unit_price;
        } else {
            showNotification('Nicht genügend Lagerbestand', 'error');
            return;
        }
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
    updateCompleteSaleButton();
}

// Update cart display
function updateCartDisplay() {
    const container = document.getElementById('cartItems');
    
    if (cart.length === 0) {
        container.innerHTML = `
            <div class="empty-cart">
                <i class="fas fa-shopping-cart"></i>
                <p>Warenkorb ist leer</p>
            </div>
        `;
    } else {
        container.innerHTML = cart.map((item, index) => `
            <div class="cart-item">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-details">${formatPrice(item.unit_price)} × ${item.quantity}</div>
                </div>
                <div class="cart-item-controls">
                    <button class="quantity-btn" onclick="updateQuantity(${index}, -1)">-</button>
                    <span class="quantity-display">${item.quantity}</span>
                    <button class="quantity-btn" onclick="updateQuantity(${index}, 1)">+</button>
                    <div class="cart-item-price">${formatPrice(item.total_price)}</div>
                    <button class="remove-item" onclick="removeFromCart(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    updateCartTotal();
}

// Update item quantity
function updateQuantity(index, change) {
    const item = cart[index];
    const product = products.find(p => p.id === item.product_id);
    
    const newQuantity = item.quantity + change;
    
    if (newQuantity <= 0) {
        removeFromCart(index);
        return;
    }
    
    if (newQuantity > product.stock) {
        showNotification('Nicht genügend Lagerbestand', 'error');
        return;
    }
    
    item.quantity = newQuantity;
    item.total_price = item.quantity * item.unit_price;
    
    updateCartDisplay();
}

// Remove item from cart
function removeFromCart(index) {
    cart.splice(index, 1);
    updateCartDisplay();
    updateCompleteSaleButton();
}

// Clear entire cart
function clearCart() {
    cart = [];
    updateCartDisplay();
    updateCompleteSaleButton();
    document.getElementById('receivedAmount').value = '';
    calculateChange();
}

// Update cart total
function updateCartTotal() {
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    document.getElementById('totalAmount').textContent = formatPrice(total);
    calculateChange();
}

// Select payment method
function selectPaymentMethod(method) {
    currentPaymentMethod = method;
    
    // Update button states
    document.querySelectorAll('.payment-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-method="${method}"]`).classList.add('active');
    
    // Show/hide cash calculation
    const cashCalc = document.getElementById('cashCalculation');
    if (method === 'Bargeld') {
        cashCalc.style.display = 'block';
    } else {
        cashCalc.style.display = 'none';
        document.getElementById('receivedAmount').value = '';
        calculateChange();
    }
    
    updateCompleteSaleButton();
}

// Calculate change
function calculateChange() {
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    const received = parseFloat(document.getElementById('receivedAmount').value) || 0;
    const change = received - total;
    
    document.getElementById('changeAmount').textContent = formatPrice(Math.max(0, change));
    updateCompleteSaleButton();
}

// Update complete sale button state
function updateCompleteSaleButton() {
    const btn = document.getElementById('completeSaleBtn');
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    
    let canComplete = cart.length > 0;
    
    if (currentPaymentMethod === 'Bargeld') {
        const received = parseFloat(document.getElementById('receivedAmount').value) || 0;
        canComplete = canComplete && received >= total;
    }
    
    btn.disabled = !canComplete;
}

// Complete sale
async function completeSale() {
    if (cart.length === 0) return;
    
    const total = cart.reduce((sum, item) => sum + item.total_price, 0);
    
    const saleData = {
        total_amount: total,
        payment_method: currentPaymentMethod,
        cashier: 'Kassierer',
        items: cart
    };
    
    try {
        const response = await fetch('/api/sales', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saleData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`Verkauf erfolgreich abgeschlossen! Verkaufs-ID: ${result.sale_id}`, 'success');
            
            // Show receipt
            showReceipt(result.sale_id, total);
            
            // Clear cart and reset
            clearCart();
            selectPaymentMethod('Bargeld');
            
            // Reload data
            loadProducts();
            loadRecentSales();
        } else {
            showNotification(`Fehler beim Abschließen des Verkaufs: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error completing sale:', error);
        showNotification('Fehler beim Abschließen des Verkaufs', 'error');
    }
}

// Show receipt
function showReceipt(saleId, total) {
    const receiptContent = `
        <div style="text-align: center; padding: 20px; background: white; border-radius: 10px; max-width: 300px; margin: 0 auto;">
            <h3>🧾 QUITTUNG</h3>
            <p><strong>Verkaufs-ID:</strong> ${saleId}</p>
            <p><strong>Datum:</strong> ${new Date().toLocaleString('de-DE')}</p>
            <hr>
            ${cart.map(item => `
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>${item.name} x${item.quantity}</span>
                    <span>${formatPrice(item.total_price)}</span>
                </div>
            `).join('')}
            <hr>
            <div style="display: flex; justify-content: space-between; font-weight: bold; font-size: 1.2em;">
                <span>GESAMT:</span>
                <span>${formatPrice(total)}</span>
            </div>
            <p><strong>Zahlungsart:</strong> ${currentPaymentMethod}</p>
            ${currentPaymentMethod === 'Bargeld' ? `
                <p><strong>Erhalten:</strong> ${formatPrice(parseFloat(document.getElementById('receivedAmount').value) || 0)}</p>
                <p><strong>Rückgeld:</strong> ${document.getElementById('changeAmount').textContent}</p>
            ` : ''}
            <p style="margin-top: 20px; font-size: 0.9em; color: #666;">Vielen Dank für Ihren Einkauf!</p>
        </div>
    `;
    
    // Create temporary modal for receipt
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.style.display = 'block';
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 400px;">
            <div class="modal-header">
                <h3>Quittung</h3>
                <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
            </div>
            <div class="modal-body">
                ${receiptContent}
                <div style="text-align: center; margin-top: 20px;">
                    <button class="btn btn-primary" onclick="window.print()">
                        <i class="fas fa-print"></i> Drucken
                    </button>
                    <button class="btn btn-secondary" onclick="this.closest('.modal').remove()">
                        Schließen
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Load recent sales
async function loadRecentSales() {
    try {
        const response = await fetch('/api/sales');
        const sales = await response.json();
        
        const container = document.getElementById('recentSales');
        container.innerHTML = sales.slice(0, 5).map(sale => `
            <div class="sale-item" onclick="showSaleDetails(${sale.id})">
                <div class="sale-item-header">
                    <span class="sale-id">#${sale.id}</span>
                    <span class="sale-amount">${formatPrice(sale.total_amount)}</span>
                </div>
                <div class="sale-details">
                    ${new Date(sale.created_at).toLocaleString('de-DE')} • ${sale.payment_method} • ${sale.item_count} Artikel
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading recent sales:', error);
    }
}

// Show sale details
async function showSaleDetails(saleId) {
    try {
        const response = await fetch(`/api/sales/${saleId}`);
        const sale = await response.json();
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.style.display = 'block';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Verkaufsdetails #${sale.id}</h3>
                    <span class="close" onclick="this.closest('.modal').remove()">&times;</span>
                </div>
                <div class="modal-body">
                    <div style="margin-bottom: 20px;">
                        <p><strong>Datum:</strong> ${new Date(sale.created_at).toLocaleString('de-DE')}</p>
                        <p><strong>Kassierer:</strong> ${sale.cashier}</p>
                        <p><strong>Zahlungsart:</strong> ${sale.payment_method}</p>
                        <p><strong>Gesamtbetrag:</strong> ${formatPrice(sale.total_amount)}</p>
                    </div>
                    <h4>Artikel:</h4>
                    <div class="product-table-container">
                        <table class="product-table">
                            <thead>
                                <tr>
                                    <th>Produkt</th>
                                    <th>Einzelpreis</th>
                                    <th>Menge</th>
                                    <th>Gesamtpreis</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${sale.items.map(item => `
                                    <tr>
                                        <td>${item.product_name}</td>
                                        <td>${formatPrice(item.unit_price)}</td>
                                        <td>${item.quantity}</td>
                                        <td>${formatPrice(item.total_price)}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    } catch (error) {
        console.error('Error loading sale details:', error);
        showNotification('Fehler beim Laden der Verkaufsdetails', 'error');
    }
}

// Product management functions
function showProductModal() {
    document.getElementById('productModal').style.display = 'block';
    updateProductTable();
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function showTab(tabName) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabName).style.display = 'block';
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function updateProductTable() {
    const tbody = document.getElementById('productTableBody');
    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.name}</td>
            <td>${formatPrice(product.price)}</td>
            <td>${product.category || '-'}</td>
            <td>${product.stock}</td>
            <td class="actions">
                <button class="btn btn-sm btn-secondary" onclick="editProduct(${product.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteProduct(${product.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

async function addNewProduct() {
    const formData = {
        name: document.getElementById('productName').value,
        price: parseFloat(document.getElementById('productPrice').value),
        category: document.getElementById('productCategory').value,
        barcode: document.getElementById('productBarcode').value,
        stock: parseInt(document.getElementById('productStock').value)
    };
    
    try {
        const response = await fetch('/api/products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Produkt erfolgreich hinzugefügt', 'success');
            document.getElementById('productForm').reset();
            loadProducts();
        } else {
            showNotification(`Fehler: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Error adding product:', error);
        showNotification('Fehler beim Hinzufügen des Produkts', 'error');
    }
}

async function deleteProduct(productId) {
    if (!confirm('Sind Sie sicher, dass Sie dieses Produkt löschen möchten?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/products/${productId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification('Produkt gelöscht', 'success');
            loadProducts();
        } else {
            showNotification('Fehler beim Löschen des Produkts', 'error');
        }
    } catch (error) {
        console.error('Error deleting product:', error);
        showNotification('Fehler beim Löschen des Produkts', 'error');
    }
}

// Reports functions
function showReports() {
    document.getElementById('reportsModal').style.display = 'block';
    document.getElementById('reportDate').value = new Date().toISOString().split('T')[0];
    loadDailyReport();
}

async function loadDailyReport() {
    const date = document.getElementById('reportDate').value;
    
    try {
        const response = await fetch(`/api/reports/daily?date=${date}`);
        const report = await response.json();
        
        const container = document.getElementById('reportContent');
        container.innerHTML = `
            <div class="report-stats">
                <div class="stat-card">
                    <div class="stat-value">${formatPrice(report.total_revenue)}</div>
                    <div class="stat-label">Gesamtumsatz</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${report.total_transactions}</div>
                    <div class="stat-label">Verkäufe</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${formatPrice(report.avg_transaction)}</div>
                    <div class="stat-label">Ø Verkaufswert</div>
                </div>
            </div>
            
            <div class="report-section">
                <h4>Zahlungsarten</h4>
                <div class="product-table-container">
                    <table class="product-table">
                        <thead>
                            <tr>
                                <th>Zahlungsart</th>
                                <th>Anzahl</th>
                                <th>Betrag</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${report.payment_summary.map(payment => `
                                <tr>
                                    <td>${payment.payment_method}</td>
                                    <td>${payment.count}</td>
                                    <td>${formatPrice(payment.amount)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="report-section">
                <h4>Meistverkaufte Produkte</h4>
                <div class="product-table-container">
                    <table class="product-table">
                        <thead>
                            <tr>
                                <th>Produkt</th>
                                <th>Verkaufte Menge</th>
                                <th>Umsatz</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${report.top_products.map(product => `
                                <tr>
                                    <td>${product.name}</td>
                                    <td>${product.quantity}</td>
                                    <td>${formatPrice(product.revenue)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Error loading report:', error);
        showNotification('Fehler beim Laden des Berichts', 'error');
    }
}

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('de-DE', {
        style: 'currency',
        currency: 'EUR'
    }).format(price);
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        animation: slideInRight 0.3s ease;
    `;
    
    // Set background color based on type
    switch (type) {
        case 'success':
            notification.style.background = '#4CAF50';
            break;
        case 'error':
            notification.style.background = '#f44336';
            break;
        case 'warning':
            notification.style.background = '#ff9800';
            break;
        default:
            notification.style.background = '#2196F3';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);