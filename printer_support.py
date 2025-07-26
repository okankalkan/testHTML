import win32print
import win32ui
import win32con
import win32gui
from datetime import datetime
import tempfile
import os

class EpsonTMT88VPrinter:
    """
    Windows Printer Support für Epson TMT88V Thermodrucker
    Unterstützt ESC/POS Kommandos für optimale Belegdrucke
    """
    
    def __init__(self, printer_name=None):
        """
        Initialisiert den Drucker
        :param printer_name: Name des Druckers (None = Standarddrucker)
        """
        self.printer_name = printer_name or self.get_default_printer()
        self.width_chars = 48  # Standard Zeichen pro Zeile für TMT88V
        
    def get_default_printer(self):
        """Gibt den Standarddrucker zurück"""
        try:
            return win32print.GetDefaultPrinter()
        except:
            # Fallback: Ersten verfügbaren Drucker nehmen
            printers = self.list_printers()
            return printers[0] if printers else None
    
    def list_printers(self):
        """Listet alle verfügbaren Drucker auf"""
        printers = []
        for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            printers.append(printer[2])
        return printers
    
    def find_epson_printer(self):
        """Sucht automatisch nach Epson TMT88V Drucker"""
        printers = self.list_printers()
        epson_keywords = ['epson', 'tmt88', 'tm-t88', 'thermal', 'receipt']
        
        for printer in printers:
            printer_lower = printer.lower()
            if any(keyword in printer_lower for keyword in epson_keywords):
                return printer
        return None
    
    def print_receipt(self, sale_data):
        """
        Druckt einen Beleg mit ESC/POS Formatierung
        :param sale_data: Dictionary mit Verkaufsdaten
        """
        try:
            # ESC/POS Beleg erstellen
            receipt_text = self.format_receipt(sale_data)
            
            # Über Windows Druckerspooler drucken
            self.print_text(receipt_text)
            
            return {'success': True, 'message': 'Beleg erfolgreich gedruckt'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def format_receipt(self, sale_data):
        """
        Formatiert den Beleg im ESC/POS Format
        """
        lines = []
        
        # Header mit Logo/Firmenname
        lines.append(self.center_text("=" * 48))
        lines.append(self.center_text("KASSENSYSTEM"))
        lines.append(self.center_text("Ihr Geschäft"))
        lines.append(self.center_text("=" * 48))
        lines.append("")
        
        # Verkaufsinformationen
        now = datetime.now()
        lines.append(f"Datum: {now.strftime('%d.%m.%Y %H:%M:%S')}")
        lines.append(f"Beleg-Nr: {sale_data.get('sale_id', 'N/A')}")
        lines.append(f"Kassierer: {sale_data.get('cashier', 'System')}")
        lines.append("-" * 48)
        
        # Artikel
        lines.append("ARTIKEL")
        lines.append("-" * 48)
        
        total = 0
        for item in sale_data.get('items', []):
            name = item.get('name', 'Unbekannt')
            qty = item.get('quantity', 1)
            price = item.get('unit_price', 0)
            total_price = item.get('total_price', 0)
            
            # Artikelzeile
            lines.append(f"{name[:30]:<30}")
            lines.append(f"  {qty} x {self.format_price(price)} = {self.format_price(total_price):>12}")
            
            total += total_price
        
        lines.append("-" * 48)
        
        # Summe
        lines.append(f"{'GESAMT:':>36} {self.format_price(total):>10}")
        lines.append("")
        
        # Zahlungsinformation
        payment_method = sale_data.get('payment_method', 'Bargeld')
        lines.append(f"Zahlungsart: {payment_method}")
        
        if payment_method == 'Bargeld':
            received = sale_data.get('received_amount', total)
            change = received - total
            lines.append(f"Erhalten:    {self.format_price(received):>10}")
            if change > 0:
                lines.append(f"Rückgeld:    {self.format_price(change):>10}")
        
        lines.append("")
        lines.append(self.center_text("Vielen Dank für Ihren Einkauf!"))
        lines.append(self.center_text("Beleg bitte aufbewahren"))
        lines.append("")
        
        # MwSt Hinweis
        lines.append(self.center_text("Alle Preise inkl. 19% MwSt"))
        lines.append("")
        
        # Footer
        lines.append(self.center_text("=" * 48))
        
        # Papier vorschub
        lines.extend(["", "", "", ""])
        
        return "\n".join(lines)
    
    def print_text(self, text):
        """
        Druckt Text über Windows Druckerspooler
        """
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_file = f.name
        
        try:
            # Drucker öffnen
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                # Druckjob starten
                job_info = ("Kassensystem Beleg", None, "")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Text als Raw Data senden (für Thermodrucker optimal)
                    with open(temp_file, 'rb') as f:
                        data = f.read()
                    
                    win32print.WritePrinter(hprinter, data)
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
                
        finally:
            # Temporäre Datei löschen
            try:
                os.unlink(temp_file)
            except:
                pass
    
    def print_raw_escpos(self, commands):
        """
        Sendet rohe ESC/POS Kommandos an den Drucker
        :param commands: Bytes mit ESC/POS Kommandos
        """
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                job_info = ("ESC/POS Commands", None, "RAW")
                job_id = win32print.StartDocPrinter(hprinter, 1, job_info)
                
                try:
                    win32print.StartPagePrinter(hprinter)
                    win32print.WritePrinter(hprinter, commands)
                    win32print.EndPagePrinter(hprinter)
                    
                finally:
                    win32print.EndDocPrinter(hprinter)
                    
            finally:
                win32print.ClosePrinter(hprinter)
                
            return True
            
        except Exception as e:
            print(f"Druckfehler: {e}")
            return False
    
    def cut_paper(self):
        """Schneidet das Papier"""
        # ESC/POS Kommando für Papier schneiden
        cut_command = b'\x1d\x56\x00'  # GS V 0 (Vollschnitt)
        return self.print_raw_escpos(cut_command)
    
    def open_cash_drawer(self):
        """Öffnet die Kassenschublade"""
        # ESC/POS Kommando für Kassenschublade
        drawer_command = b'\x1b\x70\x00\x32\x96'  # ESC p 0 50 150
        return self.print_raw_escpos(drawer_command)
    
    def print_test_page(self):
        """Druckt eine Testseite"""
        test_data = {
            'sale_id': 'TEST-001',
            'cashier': 'System Test',
            'payment_method': 'Bargeld',
            'received_amount': 10.00,
            'items': [
                {
                    'name': 'Test Artikel 1',
                    'quantity': 2,
                    'unit_price': 1.50,
                    'total_price': 3.00
                },
                {
                    'name': 'Test Artikel 2',
                    'quantity': 1,
                    'unit_price': 2.99,
                    'total_price': 2.99
                }
            ]
        }
        
        return self.print_receipt(test_data)
    
    def center_text(self, text):
        """Zentriert Text für den Drucker"""
        if len(text) >= self.width_chars:
            return text
        padding = (self.width_chars - len(text)) // 2
        return " " * padding + text
    
    def format_price(self, price):
        """Formatiert Preise"""
        return f"{price:.2f}€"
    
    def get_printer_status(self):
        """Gibt den Druckerstatus zurück"""
        try:
            hprinter = win32print.OpenPrinter(self.printer_name)
            try:
                status = win32print.GetPrinter(hprinter, 2)
                return {
                    'online': True,
                    'name': status['pPrinterName'],
                    'status': status['Status'],
                    'jobs': status['cJobs']
                }
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            return {
                'online': False,
                'error': str(e)
            }


# Flask Integration
def add_printer_routes(app):
    """
    Fügt Drucker-Routen zur Flask App hinzu
    """
    @app.route('/api/printer/status')
    def printer_status():
        printer = EpsonTMT88VPrinter()
        status = printer.get_printer_status()
        return {'printer': status}
    
    @app.route('/api/printer/test', methods=['POST'])
    def print_test():
        printer = EpsonTMT88VPrinter()
        result = printer.print_test_page()
        return result
    
    @app.route('/api/printer/receipt', methods=['POST'])
    def print_receipt():
        from flask import request
        data = request.json
        printer = EpsonTMT88VPrinter()
        result = printer.printer_receipt(data)
        return result
    
    @app.route('/api/printer/cut')
    def cut_paper():
        printer = EpsonTMT88VPrinter()
        success = printer.cut_paper()
        return {'success': success}
    
    @app.route('/api/printer/drawer')
    def open_drawer():
        printer = EpsonTMT88VPrinter()
        success = printer.open_cash_drawer()
        return {'success': success}


# Beispiel Verwendung
if __name__ == "__main__":
    # Drucker initialisieren
    printer = EpsonTMT88VPrinter()
    
    print("Verfügbare Drucker:")
    for p in printer.list_printers():
        print(f"  - {p}")
    
    print(f"\nAktueller Drucker: {printer.printer_name}")
    
    # Epson Drucker suchen
    epson = printer.find_epson_printer()
    if epson:
        print(f"Epson Drucker gefunden: {epson}")
        printer.printer_name = epson
    
    # Status prüfen
    status = printer.get_printer_status()
    print(f"Drucker Status: {status}")
    
    # Testdruck
    print("\nTestdruck wird gesendet...")
    result = printer.print_test_page()
    print(f"Testdruck Ergebnis: {result}")