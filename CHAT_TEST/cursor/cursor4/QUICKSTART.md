# Quick Start Guide

Get your Real-time Chat System up and running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

### Option A: Using the startup script (Recommended)
```bash
python start_server.py
```

### Option B: Using uvicorn directly
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Option C: Using Python directly
```bash
cd backend
python main.py
```

## Step 3: Open the Application

Open your web browser and navigate to:
```
http://localhost:8000
```

That's it! 🎉

## Testing the Application

Run the automated test suite:
```bash
pytest tests/ -v
```

Expected output: **12 tests passed**

## What to Try

1. **Create your first room:**
   - Enter a username
   - Click "Create Room" and give it a name
   - Start chatting!

2. **Test real-time features:**
   - Open the app in two browser windows/tabs
   - Join the same room with different usernames
   - Send messages and see them appear instantly
   - Try typing to see the typing indicator

3. **Explore the API:**
   - Visit http://localhost:8000/docs for interactive API documentation
   - Try the REST endpoints directly from the Swagger UI

## Troubleshooting

**Port already in use?**
```bash
# Change the port in start_server.py or use:
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Dependencies not installing?**
```bash
# Try upgrading pip first:
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Tests failing?**
```bash
# Make sure no server is running, then:
pytest tests/ -v --tb=short
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out the API documentation at http://localhost:8000/docs
- Modify the frontend in `frontend/` directory
- Extend the backend in `backend/` directory
- Add more tests in `tests/` directory

Enjoy your real-time chat system! 💬

