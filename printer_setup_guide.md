# 🖨️ Epson TMT88V Drucker Setup Guide

## 📋 **Übersicht**
Vollständige Anleitung zur Integration Ihres Epson TMT88V Thermodruckers mit dem Kassensystem.

## 🔧 **Hardware Setup**

### **1. Drucker anschließen**
- **USB-Kabel** mit Computer verbinden
- **Stromkabel** anschließen
- **Papierrolle** einlegen (Thermobeleg-Rollen 80mm)
- **Drucker einschalten** (Power-LED leuchtet)

### **2. Windows Treiber installieren**
1. **Epson Website** besuchen: https://epson.de
2. **TMT88V Treiber** herunterladen für Ihr Windows
3. **Treiber installieren** (als Administrator ausführen)
4. **Drucker testen** über Windows-Druckereinstellungen

### **3. Drucker konfigurieren**
- **Standarddrucker** setzen (optional)
- **Papierformat**: 80mm Thermorolle
- **Druckqualität**: Standard
- **ESC/POS Modus** aktivieren

## 💻 **Software Installation**

### **1. Python Dependencies installieren**
```bash
pip install -r requirements_with_printer.txt
```

**Oder einzeln:**
```bash
pip install Flask==2.3.3
pip install Flask-CORS==4.0.0
pip install pywin32==306
```

### **2. Kassensystem mit Drucker starten**
```bash
python app_with_printer.py
```

### **3. Drucker-Status prüfen**
Nach dem Start sehen Sie:
```
🚀 Kassensystem mit Druckfunktion startet...
💻 Webinterface: http://localhost:5000
🖨️  Drucker-Support: Aktiviert
🖨️  Aktueller Drucker: EPSON TM-T88V Receipt
🖨️  Epson TMT88V gefunden: EPSON TM-T88V Receipt
```

## 🌐 **Web-Interface Funktionen**

### **Automatische Funktionen:**
- ✅ **Automatischer Belegdruck** nach jedem Verkauf
- ✅ **Drucker-Erkennung** beim Start
- ✅ **Fehlerbehandlung** bei Druckproblemen
- ✅ **Status-Überwachung** des Druckers

### **Manuelle Funktionen:**
- 🖨️ **Beleg nachdrucken** (`/api/sales/{id}/print`)
- ✂️ **Papier schneiden** (`/api/printer/cut`)
- 💰 **Kassenschublade öffnen** (`/api/printer/drawer`)
- 🧾 **Testdruck** (`/api/printer/test`)

## 📊 **API Endpunkte**

### **Drucker-Status**
```http
GET /api/printer/status
```
**Antwort:**
```json
{
  "printer": {
    "online": true,
    "name": "EPSON TM-T88V Receipt",
    "status": 0,
    "jobs": 0
  }
}
```

### **Testdruck**
```http
POST /api/printer/test
```
**Antwort:**
```json
{
  "success": true,
  "message": "Beleg erfolgreich gedruckt"
}
```

### **Beleg drucken**
```http
POST /api/printer/receipt
```
**Body:**
```json
{
  "sale_id": 123,
  "total_amount": 15.50,
  "payment_method": "Bargeld",
  "cashier": "Max Mustermann",
  "items": [
    {
      "name": "Artikel 1",
      "quantity": 2,
      "unit_price": 5.00,
      "total_price": 10.00
    }
  ]
}
```

### **Beleg nachdrucken**
```http
POST /api/sales/123/print
```

### **Papier schneiden**
```http
GET /api/printer/cut
```

### **Kassenschublade öffnen**
```http
GET /api/printer/drawer
```

## 🎯 **Beleg-Format**

### **Standard Beleg Layout:**
```
================================================
                KASSENSYSTEM
                Ihr Geschäft
================================================

Datum: 25.07.2025 15:30:22
Beleg-Nr: 123
Kassierer: Max Mustermann
------------------------------------------------
ARTIKEL
------------------------------------------------
Apfel
  2 x 0,50€ =         1,00€
Brot
  1 x 2,50€ =         2,50€
------------------------------------------------
                            GESAMT:      3,50€

Zahlungsart: Bargeld
Erhalten:               5,00€
Rückgeld:               1,50€

        Vielen Dank für Ihren Einkauf!
          Beleg bitte aufbewahren

         Alle Preise inkl. 19% MwSt

================================================
```

## 🔧 **Erweiterte Konfiguration**

### **Eigenen Drucker konfigurieren:**
```python
from printer_support import EpsonTMT88VPrinter

# Spezifischen Drucker verwenden
printer = EpsonTMT88VPrinter("EPSON TM-T88V Receipt")

# Verfügbare Drucker auflisten
printers = printer.list_printers()
print(printers)

# Epson Drucker automatisch finden
epson = printer.find_epson_printer()
```

### **Beleg-Layout anpassen:**
In `printer_support.py` → `format_receipt()` Methode:
```python
# Header anpassen
lines.append(self.center_text("IHR FIRMENNAME"))
lines.append(self.center_text("Ihre Adresse"))
lines.append(self.center_text("Tel: 01234/56789"))

# Footer anpassen
lines.append(self.center_text("Öffnungszeiten: Mo-Fr 8-18 Uhr"))
```

## 🛠️ **Problembehandlung**

### **Drucker wird nicht erkannt:**
1. **USB-Verbindung** prüfen
2. **Treiber neu installieren**
3. **Windows Druckerspooler** neu starten
4. **Drucker als Standard** setzen

### **Druckfehler:**
```bash
Druckfehler: [Errno 2] No such file or directory
```
**Lösung:** Drucker-Treiber installieren

### **ESC/POS Kommandos funktionieren nicht:**
```bash
# RAW-Druck aktivieren
job_info = ("ESC/POS Commands", None, "RAW")
```

### **Kassenschublade öffnet nicht:**
- **RJ12-Kabel** korrekt angeschlossen?
- **Schublade** kompatibel mit Epson TMT88V?
- **ESC/POS Kommando** korrekt: `\x1b\x70\x00\x32\x96`

## ⚡ **Performance Optimierung**

### **Drucker-Initialisierung beim Start:**
```python
# Globale Drucker-Instanz
PRINTER = None

def get_printer():
    global PRINTER
    if PRINTER is None:
        PRINTER = EpsonTMT88VPrinter()
    return PRINTER
```

### **Asynchrones Drucken:**
```python
import threading

def async_print(sale_data):
    def print_task():
        printer = EpsonTMT88VPrinter()
        printer.print_receipt(sale_data)
    
    thread = threading.Thread(target=print_task)
    thread.start()
```

## 📱 **Mobile Integration**

### **JavaScript Print-Trigger:**
```javascript
// Nach erfolgreichem Verkauf
async function completeSale() {
    const sale = await createSale(saleData);
    
    if (sale.success) {
        // Automatischer Druck (bereits integriert)
        showNotification('Verkauf abgeschlossen - Beleg wird gedruckt');
    }
}

// Manueller Nachdruck
async function reprintReceipt(saleId) {
    const response = await fetch(`/api/sales/${saleId}/print`, {
        method: 'POST'
    });
    const result = await response.json();
    
    if (result.success) {
        showNotification('Beleg nachgedruckt');
    }
}
```

## 🔍 **Debugging**

### **Drucker-Status testen:**
```python
python printer_support.py
```

**Ausgabe:**
```
Verfügbare Drucker:
  - Microsoft Print to PDF
  - EPSON TM-T88V Receipt
  - OneNote (Desktop)

Aktueller Drucker: EPSON TM-T88V Receipt
Epson Drucker gefunden: EPSON TM-T88V Receipt
Drucker Status: {'online': True, 'name': 'EPSON TM-T88V Receipt', 'status': 0, 'jobs': 0}

Testdruck wird gesendet...
Testdruck Ergebnis: {'success': True, 'message': 'Beleg erfolgreich gedruckt'}
```

### **Log-Ausgaben aktivieren:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In print_receipt Methode
logger.debug(f"Drucke Beleg für Verkauf {sale_id}")
```

## 📦 **Production Deployment**

### **Windows Service Setup:**
```bash
# NSSM (Non-Sucking Service Manager) installieren
nssm install KassensystemService
nssm set KassensystemService Application "C:\Python\python.exe"
nssm set KassensystemService AppParameters "C:\Kassensystem\app_with_printer.py"
nssm start KassensystemService
```

### **Firewall Konfiguration:**
- **Port 5000** für HTTP-Zugriff freigeben
- **Drucker-Ports** (USB/Parallel) freigeben

### **Backup Strategie:**
- **Datenbank** täglich sichern: `kassensystem.db`
- **Konfiguration** sichern: `printer_support.py`
- **Belege** digital archivieren

---

## ✅ **Quick-Start Checklist**

- [ ] Epson TMT88V angeschlossen und eingeschaltet
- [ ] Windows-Treiber installiert
- [ ] `pip install pywin32` ausgeführt
- [ ] `python app_with_printer.py` gestartet
- [ ] Drucker im Kassensystem erkannt
- [ ] Testdruck erfolgreich
- [ ] Kassenschublade funktioniert (optional)
- [ ] Automatischer Druck bei Verkäufen aktiv

**🎉 Ihr Kassensystem mit Epson TMT88V ist jetzt einsatzbereit!**