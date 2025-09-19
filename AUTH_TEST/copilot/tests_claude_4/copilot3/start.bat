@echo off
REM Start the authentication application on Windows

echo Starting Full-Stack Authentication App...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

REM Start the backend server
echo Starting backend server on http://localhost:8000...
start "Backend Server" cmd /k "python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend server
echo Starting frontend server on http://localhost:3000...
cd ..\frontend
start "Frontend Server" cmd /k "python -m http.server 3000"

echo.
echo ✅ Application started successfully!
echo 🖥️  Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📖 API Docs: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause >nul