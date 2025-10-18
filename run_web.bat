@echo off
REM SlideNarrator - Quick Start Script for Web Interface (Windows)

echo 🎤 SlideNarrator - Starting Web Application...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Virtual environment not found. Creating one...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo 📥 Installing dependencies...
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo ✅ Setup complete!
echo.
echo 🌐 Launching SlideNarrator web interface...
echo    Access the app at: http://localhost:8501
echo.
echo    Press Ctrl+C to stop the server
echo.

REM Run Streamlit
streamlit run app.py
