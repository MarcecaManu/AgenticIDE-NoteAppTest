@echo off
REM Setup script for Real-time Chat System (Windows)

echo Setting up Real-time Chat System...
echo.

REM Install backend dependencies
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
cd ..

REM Install test dependencies
echo Installing test dependencies...
cd tests
pip install -r requirements.txt
cd ..

echo.
echo Setup complete!
echo.
echo To start the server, run:
echo   cd backend
echo   uvicorn main:app --reload --host 0.0.0.0 --port 8000
echo.
echo Then open your browser to: http://localhost:8000
echo.
echo To run tests:
echo   pytest tests/ -v
echo.
pause

