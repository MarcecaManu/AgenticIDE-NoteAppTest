@echo off
echo ========================================
echo   Full-Stack Authentication Demo
echo ========================================
echo.
echo Starting FastAPI backend server...
echo Backend will be available at: http://localhost:8000
echo API documentation at: http://localhost:8000/docs
echo.
echo To view the frontend:
echo 1. Open frontend/index.html in your browser
echo 2. Or serve it with: python -m http.server 3000 (from frontend folder)
echo.
echo Press Ctrl+C to stop the server
echo.
cd backend
python main.py