# Maker Circulars - Data Management Platform
# PowerShell Startup Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  MAKER CIRCULARS - Data Management Platform" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "[OK] Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Create directories
if (-not (Test-Path "data")) { New-Item -ItemType Directory -Path "data" | Out-Null }
if (-not (Test-Path "uploads")) { New-Item -ItemType Directory -Path "uploads" | Out-Null }

# Setup Python virtual environment
if (-not (Test-Path ".venv")) {
    Write-Host "[SETUP] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "[SETUP] Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "[SETUP] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet

# Install frontend dependencies
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "[SETUP] Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location frontend
    cmd /c npm install
    Pop-Location
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting Backend Server (port 8000)..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Start backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD'; & .\.venv\Scripts\Activate.ps1; Set-Location backend; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Starting Frontend Dev Server (port 5173)..." -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

# Start frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$PWD\frontend'; cmd /c npm run dev" -WindowStyle Normal

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  APPLICATION STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  " -NoNewline; Write-Host "http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Backend:   " -NoNewline; Write-Host "http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:  " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Database:  " -NoNewline; Write-Host "data/maker_circulars.db" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Open http://localhost:5173 in your browser"
Write-Host "  2. Click 'Import Excel' to upload your .xlsx file"
Write-Host "  3. Preview and confirm the import"
Write-Host "  4. Manage your data!"
Write-Host ""

# Open in browser
Start-Process "http://localhost:5173"

Write-Host "Press Enter to exit this script (servers will continue running)..."
Read-Host
