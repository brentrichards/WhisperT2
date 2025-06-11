@echo off
REM Startup script for Whisper Transcription App
REM This script sets up and runs the Streamlit application

echo.
echo ============================================
echo   Whisper Transcription App
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or later.
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if we're in the right directory
if not exist "main.py" (
    echo ❌ main.py not found. Please run this script from the WhisperT2 directory.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 🔍 Checking dependencies...
python -c "import streamlit, whisper, yt_dlp, docx" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies.
        pause
        exit /b 1
    )
)

REM Run tests to ensure everything works
echo 🧪 Running quick tests...
python test_app.py >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some tests failed, but continuing anyway...
) else (
    echo ✅ All tests passed!
)

REM Start the application
echo.
echo 🚀 Starting Whisper Transcription App...
echo.
echo    The app will open in your default web browser.
echo    If it doesn't open automatically, visit:
echo    http://localhost:8501
echo.
echo    Press Ctrl+C to stop the application.
echo.

REM Start Streamlit
streamlit run main.py

echo.
echo 👋 Application stopped. Thanks for using Whisper Transcription App!
pause
