@echo off
echo Starting Frontend Server...
echo.
echo The frontend will be available at http://localhost:3000
echo.
call .\.venv\Scripts\activate
cd frontend
python -m http.server 3000

