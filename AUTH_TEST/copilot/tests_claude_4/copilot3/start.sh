#!/bin/bash
# Start the authentication application

echo "Starting Full-Stack Authentication App..."

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Error: Python is not installed or not in PATH"
    exit 1
fi

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt

# Start the backend server in background
echo "Starting backend server on http://localhost:8000..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if we have a simple HTTP server available
if command -v python &> /dev/null; then
    echo "Starting frontend server on http://localhost:3000..."
    cd ../frontend
    python -m http.server 3000 &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ Application started successfully!"
    echo "🖥️  Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all servers"
    
    # Wait for user to stop
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT
    wait
else
    echo "Backend started on http://localhost:8000"
    echo "Please open frontend/index.html in your browser manually"
    echo "Press Ctrl+C to stop the backend server"
    
    trap "kill $BACKEND_PID 2>/dev/null; exit 0" INT
    wait $BACKEND_PID
fi