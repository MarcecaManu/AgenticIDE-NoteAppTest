@echo off
echo Starting Real-time Chat Backend...
cd backend
start cmd /k "python main.py"
cd ..

timeout /t 3

echo Starting Frontend Server...
cd frontend
start cmd /k "python -m http.server 3000"
cd ..

echo.
echo ========================================
echo Backend running at: http://localhost:8000
echo Frontend running at: http://localhost:3000
echo API docs at: http://localhost:8000/docs
echo ========================================
echo.
echo Open http://localhost:3000 in your browser to use the chat!
echo Press any key to exit...
pause > nul
