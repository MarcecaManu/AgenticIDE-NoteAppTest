@echo off
echo Starting FastAPI Backend Server...
echo.
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
uvicorn backend.main:app --reload

