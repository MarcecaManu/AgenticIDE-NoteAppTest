# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

Open a terminal in the project root and run:

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Start the Application

**Option A - Use the start script (Windows):**
```bash
start.bat
```

**Option B - Manual start:**

Terminal 1 (Backend):
```bash
cd backend
python main.py
```

Terminal 2 (Frontend):
```bash
cd frontend
python -m http.server 3000
```

### Step 3: Open the Chat

Open your browser and go to: **http://localhost:3000**

---

## 🧪 Run Tests

```bash
cd backend
pytest ../tests/test_chat_system.py -v
```

Expected output: **16 tests passed** ✅

---

## 📝 Quick Test

1. Open **http://localhost:3000** in two browser tabs
2. Enter different usernames in each tab (e.g., "Alice" and "Bob")
3. Create a room in one tab (e.g., "Test Room")
4. Join the same room from the other tab
5. Start chatting - messages appear in real-time!
6. Try typing to see the typing indicator

---

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🛠️ Troubleshooting

**"Port already in use"**
- Change the port in `backend/main.py` (line 165) from 8000 to another port
- Update `frontend/app.js` API_BASE constant to match

**"Connection failed"**
- Make sure the backend is running first
- Check that you're using the correct URLs (http://localhost:8000 and http://localhost:3000)

**Tests fail**
- Delete any existing `test.db` file in the backend directory
- Reinstall dependencies: `pip install -r backend/requirements.txt`

---

## ✨ Features to Explore

- ✅ Multiple chat rooms
- ✅ Real-time messaging
- ✅ See who's online
- ✅ Typing indicators
- ✅ Message history
- ✅ Auto-reconnect on connection loss
- ✅ Join/leave notifications

---

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.
