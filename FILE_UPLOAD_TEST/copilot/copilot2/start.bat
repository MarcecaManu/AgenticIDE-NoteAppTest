@echo off
echo Starting File Upload & Management System
echo =======================================

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt

echo.
echo Starting FastAPI backend server...
start cmd /k "python main.py"

echo.
echo Backend started at http://localhost:8000
echo API documentation available at http://localhost:8000/docs
echo.

echo Starting frontend server...
cd ..\frontend
start cmd /k "python -m http.server 3000"

echo.
echo Frontend started at http://localhost:3000
echo.
echo Both servers are now running!
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul