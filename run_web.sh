#!/bin/bash

# SlideNarrator - Quick Start Script for Web Interface

echo "🎤 SlideNarrator - Starting Web Application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "🌐 Launching SlideNarrator web interface..."
echo "   Access the app at: http://localhost:8501"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""

# Run Streamlit
streamlit run app.py
