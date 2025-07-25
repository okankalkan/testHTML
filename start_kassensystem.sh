#!/bin/bash

echo "🚀 Kassensystem wird gestartet..."
echo ""

# Check if dependencies are installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installiere Dependencies..."
    pip install --break-system-packages Flask Flask-CORS
fi

# Get IP address
IP=$(hostname -I | awk '{print $1}')

echo "💰 Kassensystem startet..."
echo ""
echo "🌐 Zugriff über folgende URLs:"
echo "   👉 http://localhost:5000"
echo "   👉 http://$IP:5000"
echo "   👉 http://0.0.0.0:5000"
echo ""
echo "📱 Für Remote-Zugriff: Port 5000 weiterleiten"
echo "🛑 Zum Beenden: Ctrl+C drücken"
echo ""
echo "📊 Lade Kassensystem..."

# Start the application
python3 app.py