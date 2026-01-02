@echo off
echo Starting Real-time Chat Frontend...
cd frontend
echo.
echo Frontend server starting on http://localhost:8080
echo Make sure the backend is running on http://localhost:8000
echo.
python -m http.server 8080

