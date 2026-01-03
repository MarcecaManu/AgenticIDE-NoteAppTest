@echo off
echo Starting FastAPI Backend Server...
echo.
call .\.venv\Scripts\activate
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

