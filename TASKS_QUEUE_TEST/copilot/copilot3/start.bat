@echo off
echo ========================================
echo Task Queue System - Quick Start
echo ========================================
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)
echo.

echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo ========================================
echo Starting Task Queue Server...
echo ========================================
echo.
echo Server will be available at: http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd backend
python run_server.py
