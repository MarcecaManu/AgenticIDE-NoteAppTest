# Real-time Chat System

A full-stack real-time chat application built with FastAPI WebSockets backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI + WebSockets)
- **REST API** at `/api/chat/` for chat history and room management
- **WebSocket endpoint** at `/ws/chat/{room_id}` for real-time messaging
- **Persistent storage** using SQLite for rooms and messages
- **Connection management** with online user tracking
- **Real-time features**: message broadcasting, typing indicators, join/leave notifications

### Frontend (HTML + JavaScript)
- **Modern UI** with gradient design and smooth animations
- **Real-time messaging** with WebSocket connection
- **Room management**: create, join, delete chat rooms
- **Online users** display with live updates
- **Typing indicators** to show when users are typing
- **Message history** loaded when joining rooms
- **Auto-reconnection** on connection failures
- **Responsive design** for all screen sizes

### REST API Endpoints

#### POST /api/chat/rooms
Create a new chat room
```json
Request: {"name": "Room Name"}
Response: {"id": "uuid", "name": "Room Name", "created_at": "timestamp"}
```

#### GET /api/chat/rooms
List all chat rooms
```json
Response: [{"id": "uuid", "name": "Room Name", "created_at": "timestamp"}]
```

#### GET /api/chat/rooms/{room_id}/messages
Get message history for a room
```json
Response: [{"id": 1, "room_id": "uuid", "username": "User", "content": "Message", "timestamp": "timestamp"}]
```

#### DELETE /api/chat/rooms/{room_id}
Delete a room and all its messages
```json
Response: {"message": "Room deleted successfully"}
```

### WebSocket Protocol

#### Connection
```
ws://localhost:8000/ws/chat/{room_id}?username={username}
```

#### Message Types

**Send Message:**
```json
{"type": "message", "content": "Hello!"}
```

**Typing Indicator:**
```json
{"type": "typing", "is_typing": true}
```

**Receive Message:**
```json
{
  "type": "message",
  "id": 1,
  "room_id": "uuid",
  "username": "User",
  "content": "Hello!",
  "timestamp": "2024-01-24T10:30:00Z"
}
```

**User Joined:**
```json
{
  "type": "user_joined",
  "username": "User",
  "timestamp": "2024-01-24T10:30:00Z",
  "online_users": ["User1", "User2"]
}
```

**User Left:**
```json
{
  "type": "user_left",
  "username": "User",
  "timestamp": "2024-01-24T10:30:00Z",
  "online_users": ["User1"]
}
```

**Typing Notification:**
```json
{
  "type": "typing",
  "username": "User",
  "is_typing": true
}
```

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application with REST and WebSocket endpoints
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html          # Main HTML interface
│   └── chat.js             # JavaScript client logic
├── tests/
│   ├── test_chat.py        # Comprehensive test suite
│   └── requirements.txt    # Test dependencies
└── README.md               # This file
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in a web browser, or serve it with a simple HTTP server:
```bash
python -m http.server 8080
```

Then visit `http://localhost:8080`

## Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
```

3. Install backend dependencies:
```bash
pip install -r ../backend/requirements.txt
```

4. Run the test suite:
```bash
pytest test_chat.py -v
```

## Test Coverage

The test suite includes 15+ comprehensive tests covering:

- ✅ **REST API endpoints**: room creation, listing, message retrieval, deletion
- ✅ **WebSocket connections**: connecting, disconnecting, reconnection handling
- ✅ **Message broadcasting**: real-time message delivery to all users in a room
- ✅ **Room management**: creating, deleting rooms with cascading message deletion
- ✅ **Multi-user scenarios**: multiple users in the same room
- ✅ **Typing indicators**: real-time typing status broadcasting
- ✅ **User presence**: join/leave notifications and online user tracking
- ✅ **Message persistence**: messages stored and retrieved correctly
- ✅ **Error handling**: nonexistent rooms, invalid requests
- ✅ **Connection management**: graceful disconnect handling

## Database Schema

### Rooms Table
```sql
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
)
```

## Security Features

- **CORS enabled** for cross-origin requests
- **Input validation** using Pydantic models
- **SQL injection prevention** with parameterized queries
- **WebSocket authentication** via username parameter
- **Graceful error handling** for all endpoints
- **Connection cleanup** on disconnect

## Usage

1. **Start the backend server** (see Installation)
2. **Open the frontend** in your browser
3. **Create or join a room** from the sidebar
4. **Enter your username** (optional, defaults to "Anonymous")
5. **Start chatting!** Messages are delivered in real-time to all users in the room

### Features in Action

- **Create rooms**: Type a room name and click "Create"
- **Join rooms**: Click on any room in the sidebar
- **Send messages**: Type and press Enter or click "Send"
- **See online users**: View who's currently in the room
- **Typing indicators**: See when others are typing
- **Delete rooms**: Click the "Delete" button on any room
- **Auto-reconnect**: Connection automatically restores if lost

## Technical Details

- **Backend**: FastAPI 0.109.0 with WebSocket support
- **Database**: SQLite with persistent storage
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Real-time**: WebSocket protocol for bidirectional communication
- **Testing**: pytest with httpx for async testing
- **Connection management**: Automatic reconnection with 3-second retry

## Performance

- **Concurrent connections**: Supports multiple users per room
- **Message broadcasting**: Efficient fan-out to all connected clients
- **Persistent storage**: All messages and rooms saved to SQLite
- **Memory efficient**: Cleanup of disconnected clients
- **Scalable**: Room-based isolation for better performance

## Future Enhancements

Possible improvements:
- User authentication and authorization
- Private messaging between users
- File and image sharing
- Message editing and deletion
- Read receipts and message status
- Room permissions and moderation
- Message search and filtering
- Emoji support and reactions
- Voice and video chat integration

## License

This project is provided as-is for educational and demonstration purposes.
