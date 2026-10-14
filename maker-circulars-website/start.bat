@echo off
title Maker Circulars - Data Management Platform
echo ============================================================
echo   MAKER CIRCULARS - Data Management Platform
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js 18+ from https://nodejs.org
    pause
    exit /b 1
)

REM Create data directory
if not exist "data" mkdir data

REM Create uploads directory
if not exist "uploads" mkdir uploads

REM Setup Python virtual environment
if not exist ".venv" (
    echo [SETUP] Creating Python virtual environment...
    python -m venv .venv
)

echo [SETUP] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [SETUP] Installing Python dependencies...
pip install -r requirements.txt --quiet

REM Install frontend dependencies
if not exist "frontend\node_modules" (
    echo [SETUP] Installing frontend dependencies...
    cd frontend
    call npm.cmd install
    cd ..
)

echo.
echo ============================================================
echo   Starting Backend Server (port 8000)...
echo ============================================================
start "Backend Server" cmd /k "(if exist .venv\Scripts\activate.bat call .venv\Scripts\activate.bat) && python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo   Starting Frontend Dev Server (port 5173)...
echo ============================================================
start "Frontend Server" cmd /k "cd frontend && npm.cmd run dev"

REM Wait for frontend to start
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo   APPLICATION STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo   Database:  data/maker_circulars.db
echo.
echo   1. Open http://localhost:5173 in your browser
echo   2. Click "Import Excel" to upload your .xlsx file
echo   3. Preview and confirm the import
echo   4. Manage your data!
echo.
echo   Press any key to open the application in your browser...
pause >nul
start http://localhost:5173
