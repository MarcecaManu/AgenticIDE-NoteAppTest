#!/bin/bash

echo "Starting Real-time Chat Backend..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

sleep 3

echo "Starting Frontend Server..."
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "Backend running at: http://localhost:8000"
echo "Frontend running at: http://localhost:3000"
echo "API docs at: http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Open http://localhost:3000 in your browser to use the chat!"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
