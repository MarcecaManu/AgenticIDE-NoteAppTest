@echo off
echo Starting Frontend Server...
echo.
echo Frontend will be available at: http://localhost:8080
echo.
cd frontend
python -m http.server 8080

