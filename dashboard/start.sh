#!/bin/bash

# NovaOS V2 Dashboard Startup Script

echo "======================================"
echo "NovaOS V2 Visual Dashboard"
echo "======================================"
echo ""

# Check if database exists
if [ ! -f "/Users/krissanders/novaos-v2/data/novaos.db" ]; then
    echo "ERROR: Database not found at /Users/krissanders/novaos-v2/data/novaos.db"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "ERROR: Flask not installed"
    echo "Run: pip install -r ../requirements.txt"
    exit 1
fi

echo "Starting dashboard on http://localhost:5000"
echo "Press Ctrl+C to stop"
echo ""

# Start Flask app
cd "$(dirname "$0")"
python3 app.py
