# Real-time Chat System

A full-stack real-time chat application built with FastAPI (WebSockets) and vanilla JavaScript. Features include persistent message storage, real-time messaging, typing indicators, and online user tracking.

## 🚀 Features

### Backend (FastAPI + WebSockets)
- **REST API** for chat room and message management
- **WebSocket** endpoint for real-time communication
- **SQLite database** for persistent data storage
- **Concurrent connection handling** for multiple users per room
- **Automatic reconnection** handling

### Frontend (HTML + JavaScript)
- **Modern, responsive UI** with gradient design
- **Real-time messaging** with WebSocket connections
- **Online user tracking** showing who's in each room
- **Typing indicators** to show when others are typing
- **Message history** loaded when joining rooms
- **Connection status** indicators
- **Graceful error handling** with automatic reconnection

### Key Functionalities
- ✅ Create and delete chat rooms
- ✅ Join multiple rooms
- ✅ Real-time message broadcasting
- ✅ User join/leave notifications
- ✅ Typing indicators
- ✅ Persistent message storage
- ✅ Connection status management
- ✅ Automatic reconnection on disconnect

## 📁 Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI application with REST and WebSocket endpoints
│   ├── database.py       # SQLite database layer with persistent storage
│   ├── models.py         # Pydantic models for validation
│   ├── requirements.txt  # Python dependencies
│   └── chat.db          # SQLite database (auto-created)
├── frontend/
│   ├── index.html        # Main HTML structure
│   ├── styles.css        # Modern, responsive styling
│   └── app.js           # JavaScript client with WebSocket handling
├── tests/
│   ├── test_api.py       # Comprehensive test suite (10 tests)
│   └── requirements.txt  # Test dependencies
└── README.md            # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A modern web browser

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Open the frontend directory in a web browser or serve via a simple HTTP server:

**Option 1: Python HTTP Server**
```bash
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080`

**Option 2: Open directly**
Simply open `frontend/index.html` in your browser (WebSocket connections require backend to be running)

## 📡 API Documentation

### REST Endpoints

#### Create a Chat Room
```http
POST /api/chat/rooms
Content-Type: application/json

{
  "name": "General Chat"
}

Response: 201 Created
{
  "id": "uuid",
  "name": "General Chat",
  "created_at": "2024-01-01T10:00:00"
}
```

#### List All Rooms
```http
GET /api/chat/rooms

Response: 200 OK
[
  {
    "id": "uuid",
    "name": "General Chat",
    "created_at": "2024-01-01T10:00:00"
  }
]
```

#### Get Room Messages
```http
GET /api/chat/rooms/{room_id}/messages?limit=100

Response: 200 OK
[
  {
    "id": "uuid",
    "room_id": "uuid",
    "username": "alice",
    "content": "Hello!",
    "timestamp": "2024-01-01T10:00:00"
  }
]
```

#### Delete a Room
```http
DELETE /api/chat/rooms/{room_id}

Response: 204 No Content
```

### WebSocket Endpoint

#### Connect to a Room
```
ws://localhost:8000/ws/chat/{room_id}?username={username}
```

#### Message Types

**Client → Server:**
```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

```json
{
  "type": "typing"
}
```

**Server → Client:**
```json
{
  "type": "message",
  "message": {
    "id": "uuid",
    "room_id": "uuid",
    "username": "alice",
    "content": "Hello!",
    "timestamp": "2024-01-01T10:00:00"
  }
}
```

```json
{
  "type": "join",
  "username": "alice",
  "timestamp": "2024-01-01T10:00:00"
}
```

```json
{
  "type": "leave",
  "username": "bob",
  "timestamp": "2024-01-01T10:01:00"
}
```

```json
{
  "type": "user_list",
  "users": ["alice", "bob", "charlie"]
}
```

```json
{
  "type": "typing",
  "username": "alice",
  "timestamp": "2024-01-01T10:00:00"
}
```

## 🧪 Testing

The project includes a comprehensive test suite covering:
- REST endpoint functionality
- WebSocket connections
- Message broadcasting
- Room management
- Connection handling
- Database operations
- Input validation

### Run Tests

1. Install test dependencies:
```bash
cd tests
pip install -r requirements.txt
```

2. Run the test suite:
```bash
pytest test_api.py -v
```

### Test Coverage

The test suite includes 10 comprehensive tests:

1. **test_create_and_list_rooms** - Tests room creation and listing
2. **test_get_room_messages** - Tests message history retrieval
3. **test_delete_room** - Tests room deletion with cascade
4. **test_websocket_connection_and_join** - Tests WebSocket connection and join notifications
5. **test_websocket_message_broadcasting** - Tests real-time message broadcasting to multiple users
6. **test_websocket_typing_indicators** - Tests typing indicator functionality
7. **test_websocket_leave_notification** - Tests leave notifications on disconnect
8. **test_websocket_connection_validation** - Tests connection validation (username, room existence)
9. **test_database_concurrent_operations** - Tests concurrent database operations
10. **test_room_creation_validation** - Tests input validation for room creation

## 🎯 Usage Guide

### For Users

1. **Enter Username**: Start by entering your username on the login screen

2. **Create or Join a Room**:
   - Create a new room by entering a room name and clicking "Create"
   - Join an existing room by clicking on it

3. **Chat in Real-time**:
   - Type messages in the input field and press Enter or click Send
   - See who's online in the right panel
   - Watch typing indicators when others are typing
   - View message history automatically when joining

4. **Connection Status**:
   - Green indicator: Connected
   - Red indicator: Disconnected (automatic reconnection will be attempted)

5. **Leave a Room**: Click the "← Back" button to return to the room list

6. **Delete a Room**: Click "Delete Room" (removes room and all messages)

### For Developers

#### Database Schema

**Rooms Table:**
```sql
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

**Messages Table:**
```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
);
```

#### Connection Manager

The `ConnectionManager` class handles WebSocket connections:
- Maintains a dictionary of active connections per room
- Handles user connection/disconnection
- Broadcasts messages to all users in a room
- Tracks online users per room

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` to customize:
- **CORS settings**: Modify `allow_origins` for production
- **Database path**: Change `DB_PATH` in `database.py`
- **Message limits**: Adjust `limit` parameter in message retrieval

### Frontend Configuration

Edit `frontend/app.js` to customize:
- **API_BASE**: Backend API URL (default: `http://localhost:8000`)
- **WS_BASE**: WebSocket URL (default: `ws://localhost:8000`)
- **Reconnection delay**: Modify timeout in `connectWebSocket` (default: 3000ms)

## 🚀 Deployment

### Backend Deployment

For production, use a production ASGI server:

```bash
# Install gunicorn with uvicorn worker
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

Update CORS settings in `main.py` for your domain:
```python
allow_origins=["https://yourdomain.com"]
```

### Frontend Deployment

Deploy the frontend directory to any static hosting service:
- Netlify
- Vercel
- GitHub Pages
- AWS S3 + CloudFront

Update `API_BASE` and `WS_BASE` in `app.js` to point to your production backend.

## 📝 Code Quality

The codebase follows best practices:
- **Modular architecture** with separation of concerns
- **Type hints** and Pydantic models for validation
- **Context managers** for database connections
- **Error handling** with try-catch blocks
- **Clean, readable code** with comments
- **Responsive design** with mobile support
- **Security considerations** (input escaping, connection validation)

## 🐛 Troubleshooting

### Backend Issues

**Database locked error:**
- Close other connections to the database
- Ensure only one backend instance is running

**WebSocket connection fails:**
- Check that the backend is running on port 8000
- Verify CORS settings allow your frontend origin

### Frontend Issues

**Messages not appearing:**
- Check browser console for errors
- Verify WebSocket connection status (green indicator)
- Ensure backend is running and accessible

**Reconnection loop:**
- Check that the room still exists
- Verify backend is responding to REST API calls

## 📄 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Feel free to fork, modify, and enhance this project. Suggested improvements:
- Add user authentication
- Implement private messaging
- Add file/image sharing
- Implement message reactions
- Add user profiles and avatars
- Implement message encryption
- Add message search functionality
- Implement pagination for message history

## 📧 Support

For issues and questions, please check:
1. This README documentation
2. The test suite for usage examples
3. FastAPI documentation: https://fastapi.tiangolo.com/
4. WebSocket documentation: https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API

---

**Built with ❤️ using FastAPI and vanilla JavaScript**

