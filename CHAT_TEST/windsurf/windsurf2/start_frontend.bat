@echo off
echo Starting frontend server...
cd frontend
echo.
echo Frontend is available at: http://localhost:8080
echo.
python -m http.server 8080
