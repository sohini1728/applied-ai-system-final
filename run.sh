#!/bin/bash
# Start VibeFinder Pro Web Server

cd "$(dirname "$0")" || exit 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start the Flask server
echo ""
echo "🎵 Starting VibeFinder Pro Web Server..."
echo "📱 Open http://localhost:5000 in your browser"
echo ""
python3 app.py
