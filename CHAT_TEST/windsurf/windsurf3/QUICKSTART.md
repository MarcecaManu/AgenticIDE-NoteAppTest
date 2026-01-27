# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start the Backend Server
```bash
uvicorn main:app --reload
```
The server will start at `http://localhost:8000`

### Step 3: Open the Frontend
Open `frontend/index.html` in your web browser, or serve it:
```bash
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080`

## 🧪 Run Tests
```bash
cd tests
pip install -r requirements.txt
pip install -r ../backend/requirements.txt
pytest test_chat.py -v
```

## 📝 Quick Usage

1. **Create a room**: Enter a room name in the sidebar and click "Create"
2. **Join a room**: Click on any room in the list
3. **Set your username**: Enter your name in the username field
4. **Start chatting**: Type messages and press Enter

## ✨ Features

- ✅ Real-time messaging with WebSockets
- ✅ Multiple chat rooms
- ✅ Online user tracking
- ✅ Typing indicators
- ✅ Message history persistence
- ✅ Auto-reconnection on connection loss
- ✅ Modern, responsive UI

## 🔧 Windows Shortcuts

- Run `start_backend.bat` to start the server
- Run `run_tests.bat` to execute the test suite

## 📚 API Documentation

Once the server is running, visit:
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`
