# Quick Start Guide

Get the Real-time Chat System running in 3 simple steps!

## 🚀 Quick Start (5 minutes)

### Step 1: Start the Backend

**Windows:**
```bash
start_backend.bat
```

**Linux/Mac:**
```bash
chmod +x start_backend.sh
./start_backend.sh
```

The backend will start on `http://localhost:8000`

### Step 2: Start the Frontend (in a new terminal)

**Windows:**
```bash
start_frontend.bat
```

**Linux/Mac:**
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

The frontend will start on `http://localhost:8080`

### Step 3: Use the Application

1. Open your browser to `http://localhost:8080`
2. Enter a username
3. Create or join a chat room
4. Start chatting in real-time!

## 🧪 Run Tests

**Windows:**
```bash
run_tests.bat
```

**Linux/Mac:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

## 📋 Manual Setup (Alternative)

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
python -m http.server 8080
```

### Tests
```bash
pip install -r tests/requirements.txt
pip install -r backend/requirements.txt
pytest tests/test_api.py -v
```

## ✅ Verify Installation

1. Backend health check: Visit `http://localhost:8000/health`
2. API docs: Visit `http://localhost:8000/docs`
3. Frontend: Visit `http://localhost:8080`

## 🎯 First Chat

1. Open two browser windows to `http://localhost:8080`
2. Login with different usernames (e.g., "Alice" and "Bob")
3. Create a room in one window
4. Join the same room in both windows
5. Start chatting - messages appear instantly in both windows!

## 🆘 Troubleshooting

**Port already in use:**
- Backend: Change port in scripts from 8000 to another (e.g., 8001)
- Frontend: Change port from 8080 to another (e.g., 8081)

**Module not found:**
```bash
pip install -r backend/requirements.txt
```

**Can't connect to backend:**
- Make sure backend is running first
- Check `http://localhost:8000/health` returns `{"status": "healthy"}`

## 📚 Next Steps

For detailed documentation, see [README.md](README.md)

