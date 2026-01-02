# Quick Start Guide

Get your Real-time Chat System up and running in 3 simple steps!

## Step 1: Install Dependencies

**Important:** If you're using Python 3.14, make sure to upgrade to the latest compatible versions:

```bash
pip install --upgrade -r requirements.txt
```

For Python 3.12 or 3.13, you can use:
```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

### Option A: Using the startup script (Recommended)
```bash
python start_server.py
```

### Option B: Directly
```bash
cd backend
python main.py
```

## Step 3: Open Your Browser

Navigate to: **http://localhost:8000**

That's it! 🎉

## Quick Actions

### Create Your First Chat Room

1. Click **"+ New Room"** in the sidebar
2. Enter a name like "General Chat"
3. Click **"Create Room"**

### Join and Start Chatting

1. Click on the room you just created
2. Enter your username (e.g., "Alice")
3. Start sending messages!

### Test with Multiple Users

Open multiple browser windows/tabs to simulate different users:
- Window 1: Join as "Alice"
- Window 2: Join as "Bob"
- Watch messages appear in real-time! ✨

## Running Tests

```bash
python run_tests.py
```

Or directly with pytest:
```bash
cd tests
pytest test_chat_system.py -v
```

## Troubleshooting

**Port already in use?**
```bash
# The default port is 8000. If it's in use, modify the port in start_server.py
```

**Import errors?**
```bash
# Make sure you're in the project root directory
pip install -r requirements.txt
```

**WebSocket connection issues?**
- Check that the server is running
- Look for errors in the browser console (F12)
- Verify no firewall is blocking port 8000

## What's Included

✅ **4 REST API endpoints** for room and message management  
✅ **WebSocket support** for real-time messaging  
✅ **10 comprehensive tests** covering all functionality  
✅ **Persistent storage** with SQLite  
✅ **Modern responsive UI** with typing indicators  
✅ **User presence tracking**  
✅ **Auto-reconnection** on connection loss  

## Next Steps

- Check out the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs (Swagger UI)
- Review the test suite in `tests/test_chat_system.py`
- Customize the UI in `frontend/styles.css`

Happy chatting! 💬

