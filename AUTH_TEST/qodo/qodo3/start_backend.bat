@echo off
echo Starting Authentication Backend...
cd backend
python -m pip install -r requirements.txt
echo.
echo Backend dependencies installed. Starting server...
echo.
python main.py