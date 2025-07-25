# 💰 Kassensystem Web-App

Eine moderne, browserbasierte Kassensoftware mit Client-Server-Architektur. Die Anwendung bietet eine intuitive Benutzeroberfläche für Kassenvorgänge und umfassende Verwaltungsfunktionen.

## 🚀 Features

### Kassenfunktionen
- **Produktsuche**: Barcode-Scanner Support und Freitextsuche
- **Warenkorb-Management**: Hinzufügen, Entfernen, Mengen ändern
- **Zahlungsarten**: Bargeld, Karte, Kontaktlos
- **Rückgeld-Berechnung**: Automatische Berechnung bei Barzahlung
- **Quittungs-Druck**: Sofortige Belegausgabe nach Verkauf

### Produktverwaltung
- **Produktkatalog**: Vollständige Produktdatenbank
- **Lagerbestandsverwaltung**: Automatische Bestandsführung
- **Kategorie-System**: Produktgruppierung
- **Barcode-Integration**: Eindeutige Produktidentifikation

### Berichte & Statistiken
- **Tagesumsätze**: Detaillierte Verkaufsauswertungen
- **Zahlungsarten-Analyse**: Aufschlüsselung nach Zahlungsmethoden
- **Top-Produkte**: Bestseller-Analysen
- **Verkaufshistorie**: Vollständige Transaktionsübersicht

### Moderne UI/UX
- **Responsive Design**: Optimiert für Desktop, Tablet und Mobile
- **Glassmorphism Design**: Moderne Benutzeroberfläche
- **Real-time Updates**: Live-Aktualisierung aller Daten
- **Touch-friendly**: Optimiert für Touchscreen-Bedienung

## 📁 Projektstruktur

```
kassensystem/
├── app.py                 # Flask Server (Backend)
├── requirements.txt       # Python Dependencies
├── kassensystem.db       # SQLite Datenbank (wird automatisch erstellt)
├── templates/
│   └── index.html        # Haupt-HTML Template
├── static/
│   ├── css/
│   │   └── style.css     # CSS Styles
│   └── js/
│       └── app.js        # JavaScript Anwendungslogik
└── README.md
```

## 🛠️ Installation & Setup

### Voraussetzungen
- Python 3.7+
- Moderne Webbrowser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Repository klonen/downloaden**
```bash
git clone <repository-url>
cd kassensystem
```

2. **Virtuelle Umgebung erstellen (empfohlen)**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

4. **Server starten**
```bash
python app.py
```

5. **Browser öffnen**
Öffnen Sie http://localhost:5000 in Ihrem Browser

## 🔧 Konfiguration

### Server-Einstellungen
Der Server läuft standardmäßig auf:
- **Host**: `0.0.0.0` (alle Interfaces)
- **Port**: `5000`
- **Debug-Modus**: Aktiviert (in Produktion deaktivieren)

### Datenbank
- **Typ**: SQLite
- **Datei**: `kassensystem.db`
- **Automatische Initialisierung**: Ja
- **Beispieldaten**: Werden beim ersten Start geladen

## 📊 API-Endpunkte

### Produkte
- `GET /api/products` - Alle Produkte abrufen
- `POST /api/products` - Neues Produkt hinzufügen
- `PUT /api/products/<id>` - Produkt bearbeiten
- `DELETE /api/products/<id>` - Produkt löschen
- `GET /api/products/search/<barcode>` - Produkt per Barcode suchen

### Verkäufe
- `GET /api/sales` - Alle Verkäufe abrufen
- `POST /api/sales` - Neuen Verkauf erstellen
- `GET /api/sales/<id>` - Verkaufsdetails abrufen

### Berichte
- `GET /api/reports/daily?date=YYYY-MM-DD` - Tagesbericht

## 💡 Verwendung

### Grundlegende Kassenfunktionen

1. **Produkt hinzufügen**:
   - Barcode scannen/eingeben oder
   - Auf Schnellzugriff-Button klicken

2. **Warenkorb verwalten**:
   - Mengen mit +/- Buttons anpassen
   - Artikel mit X-Button entfernen
   - Gesamten Warenkorb mit "Leeren" zurücksetzen

3. **Bezahlung**:
   - Zahlungsart auswählen (Bargeld/Karte/Kontaktlos)
   - Bei Bargeld: Erhaltenen Betrag eingeben
   - "Verkauf abschließen" klicken

4. **Quittung**:
   - Automatische Anzeige nach Verkauf
   - Druckfunktion verfügbar

### Produktverwaltung

1. **Zahnrad-Button** (unten rechts) klicken
2. **Produktliste**: Alle Produkte anzeigen und verwalten
3. **Neues Produkt**: Formular ausfüllen und speichern

### Berichte einsehen

1. **"Berichte"** Button im Header klicken
2. **Datum auswählen** für Tagesbericht
3. **Automatische Aktualisierung** der Statistiken

## 🎨 Anpassungen

### Design anpassen
Bearbeiten Sie `static/css/style.css` für:
- Farben und Themes
- Layout-Anpassungen
- Responsive Breakpoints

### Funktionen erweitern
Bearbeiten Sie `static/js/app.js` für:
- Neue UI-Funktionen
- Zusätzliche Validierungen
- Custom Workflows

### Backend erweitern
Bearbeiten Sie `app.py` für:
- Neue API-Endpunkte
- Datenbankschema-Änderungen
- Business Logic

## 🔒 Sicherheit

### Produktions-Setup
Für den Produktionseinsatz:

1. **Debug-Modus deaktivieren**:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **HTTPS verwenden**:
- SSL-Zertifikat einrichten
- Reverse Proxy (nginx/Apache) konfigurieren

3. **Datenbank-Backup**:
- Regelmäßige Sicherungen von `kassensystem.db`
- Backup-Strategie implementieren

4. **Zugriffskontrolle**:
- Authentifizierung hinzufügen
- Benutzerrollen definieren

## 🐛 Troubleshooting

### Häufige Probleme

**Server startet nicht:**
- Port 5000 bereits belegt → anderen Port verwenden
- Dependencies fehlen → `pip install -r requirements.txt`

**Datenbank-Fehler:**
- Datei-Berechtigungen prüfen
- `kassensystem.db` löschen für Neustart

**Browser-Probleme:**
- Cache leeren
- JavaScript aktiviert?
- Modern Browser verwenden

**Responsive Design:**
- Mobile-Ansicht: Panels werden gestapelt
- Touch-Bedienung optimiert
- Floating Action Buttons für mobile Geräte

## 📞 Support

Bei Fragen oder Problemen:
1. README nochmals durchlesen
2. Browser-Konsole auf Fehler prüfen
3. Server-Logs analysieren
4. Issue erstellen mit detaillierter Fehlerbeschreibung

## 🚀 Roadmap

Geplante Features:
- [ ] Benutzer-Authentifizierung
- [ ] Multi-Store Support
- [ ] CSV/Excel Export
- [ ] Erweiterte Berichte
- [ ] Mobile App
- [ ] Cloud-Synchronisation
- [ ] Rabatt-System
- [ ] Kunden-Management

---

**Viel Erfolg mit Ihrem neuen Kassensystem! 💪**