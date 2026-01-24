@echo off
echo ========================================
echo File Upload & Management System Startup
echo ========================================
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "pip install -r requirements.txt && python main.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting Frontend...
cd ..\frontend
start "Frontend" cmd /k "echo Frontend is ready! Open http://localhost:3000 in your browser && python -m http.server 3000"

echo.
echo ========================================
echo System Started Successfully!
echo ========================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause >nul
