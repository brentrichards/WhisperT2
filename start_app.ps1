# PowerShell startup script for Whisper Transcription App
# This script sets up and runs the Streamlit application

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Whisper Transcription App" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Activate the Conda environment first
$condaEnvName = "whisper"
Write-Host "🔧 Activating Conda environment '$condaEnvName'..." -ForegroundColor Yellow
try {
    $condaExecutable = (Get-Command conda.exe -ErrorAction Stop).Source
    $condaHook = & $condaExecutable "shell.powershell" "hook" 2>$null
    Invoke-Expression $condaHook
    conda activate $condaEnvName | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Conda activation returned exit code $LASTEXITCODE" }
    Write-Host "✅ Conda environment '$condaEnvName' activated." -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to activate Conda environment '$condaEnvName'." -ForegroundColor Red
    Write-Host "   Ensure Conda is installed and the environment exists." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8 or later." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if we're in the right directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ main.py not found. Please run this script from the WhisperT2 directory." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if requirements are installed
Write-Host "🔍 Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import streamlit, whisper, yt_dlp, docx" 2>$null
    Write-Host "✅ All dependencies found!" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing required packages..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Run tests to ensure everything works
Write-Host "🧪 Running quick tests..." -ForegroundColor Yellow
try {
    $testResult = python test_app.py 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Some tests failed, but continuing anyway..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Could not run tests, but continuing anyway..." -ForegroundColor Yellow
}

# Start the application
Write-Host ""
Write-Host "🚀 Starting Whisper Transcription App..." -ForegroundColor Green
Write-Host ""
Write-Host "   The app will open in your default web browser." -ForegroundColor Cyan
Write-Host "   If it doesn't open automatically, visit:" -ForegroundColor Cyan
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "   Press Ctrl+C to stop the application." -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
try {
    streamlit run main.py
} catch {
    Write-Host ""
    Write-Host "❌ Failed to start Streamlit. Please check the error above." -ForegroundColor Red
}

Write-Host ""
Write-Host "👋 Application stopped. Thanks for using Whisper Transcription App!" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
