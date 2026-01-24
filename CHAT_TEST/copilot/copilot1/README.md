# Real-time Chat System

A full-stack real-time chat application built with FastAPI (backend) and vanilla HTML/CSS/JavaScript (frontend). The system features WebSocket-based real-time messaging, persistent storage, and comprehensive room management.

## Features

### Backend (FastAPI + WebSockets)
- **REST API** at `/api/chat/` for chat history and room management
- **WebSocket endpoint** at `/ws/chat/{room_id}` for real-time messaging
- **Persistent storage** using SQLite database
- **Connection management** with automatic cleanup

### REST Endpoints
- `POST /api/chat/rooms` - Create a new chat room
- `GET /api/chat/rooms` - List all chat rooms
- `GET /api/chat/rooms/{room_id}/messages` - Get message history for a room
- `DELETE /api/chat/rooms/{room_id}` - Delete a room and its messages
- `GET /api/chat/rooms/{room_id}/online` - Get list of online users

### WebSocket Features
- Join/leave room notifications
- Real-time message broadcasting to all connected users
- User typing indicators
- Connection status management
- Automatic reconnection handling

### Frontend Features
- Join/create chat rooms
- Send and receive messages in real-time
- See who's currently online in the room
- View message history when joining a room
- Handle connection failures gracefully
- Responsive design for mobile and desktop

### Message Structure
All messages include:
- `id` - Unique message identifier
- `room_id` - Room identifier
- `username` - Sender's username
- `content` - Message content
- `timestamp` - ISO 8601 timestamp

## Project Structure

```
copilot1/
├── backend/
│   ├── main.py           # FastAPI application with REST and WebSocket endpoints
│   └── database.py       # SQLite database operations
├── frontend/
│   ├── index.html        # Main HTML structure
│   ├── style.css         # CSS styling
│   └── app.js            # JavaScript client application
├── tests/
│   └── test_chat_system.py  # Automated tests (16 test cases)
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd copilot1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Server

Start the FastAPI server:

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

### Accessing the Application

1. Open your web browser
2. Navigate to: `http://localhost:8000/static/index.html`
3. Enter your username
4. Create a new room or join an existing one
5. Start chatting!

### API Documentation

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Running Tests

The project includes 16 comprehensive automated tests covering:
- REST endpoint functionality
- WebSocket connections and messaging
- Message broadcasting
- Room management
- Connection handling
- Error cases

### Run all tests:

```bash
pytest tests/test_chat_system.py -v
```

### Run specific test categories:

```bash
# Test REST endpoints only
pytest tests/test_chat_system.py::TestRESTEndpoints -v

# Test WebSocket functionality only
pytest tests/test_chat_system.py::TestWebSocketConnections -v

# Test database operations
pytest tests/test_chat_system.py::TestDatabaseOperations -v

# Test error handling
pytest tests/test_chat_system.py::TestErrorHandling -v
```

## Test Coverage

The test suite includes:

1. **REST Endpoints** (6 tests)
   - Room creation
   - Room listing
   - Message history retrieval
   - Room deletion
   - Error handling for non-existent rooms
   - Online users tracking

2. **WebSocket Connections** (6 tests)
   - Connection establishment
   - Message sending/receiving
   - Broadcasting to multiple users
   - Typing indicators
   - Join/leave notifications
   - Error handling for invalid rooms

3. **Database Operations** (2 tests)
   - Message persistence
   - Cascade deletion

4. **Error Handling** (2 tests)
   - Empty messages
   - Concurrent connections

## Architecture

### Backend Architecture

```
┌─────────────────┐
│   FastAPI App   │
├─────────────────┤
│  REST Endpoints │ ← HTTP Requests
│  WebSocket EP   │ ← WS Connections
├─────────────────┤
│ Connection Mgr  │ ← Manages active connections
├─────────────────┤
│   Database      │ ← SQLite persistence
└─────────────────┘
```

### Frontend Architecture

```
┌─────────────────┐
│    ChatApp      │
├─────────────────┤
│  UI Management  │
│  Event Handlers │
├─────────────────┤
│  REST Client    │ ← HTTP requests for rooms/history
│  WebSocket      │ ← Real-time messaging
└─────────────────┘
```

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
    id TEXT PRIMARY KEY,
    room_id TEXT NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
)
```

## WebSocket Protocol

### Client → Server Messages

**Send Message:**
```json
{
    "type": "message",
    "content": "Hello, World!"
}
```

**Typing Indicator:**
```json
{
    "type": "typing",
    "content": "typing"
}
```

### Server → Client Messages

**Message Broadcast:**
```json
{
    "type": "message",
    "id": "uuid",
    "username": "John",
    "content": "Hello!",
    "timestamp": "2026-01-02T10:30:00"
}
```

**User Joined:**
```json
{
    "type": "join",
    "username": "John",
    "content": "John joined the room",
    "timestamp": "2026-01-02T10:30:00",
    "online_users": ["John", "Jane"]
}
```

**User Left:**
```json
{
    "type": "leave",
    "username": "John",
    "content": "John left the room",
    "timestamp": "2026-01-02T10:30:00",
    "online_users": ["Jane"]
}
```

**Typing Indicator:**
```json
{
    "type": "typing",
    "username": "John"
}
```

## Features in Detail

### Real-time Messaging
- Messages are instantly broadcast to all connected users in a room
- Message history is persisted and loaded when joining a room
- Efficient WebSocket-based communication

### Room Management
- Create unlimited chat rooms
- Delete rooms (removes all associated messages)
- List all available rooms with creation timestamps

### User Experience
- Automatic reconnection on connection loss
- Visual typing indicators
- Online user list in sidebar
- Connection status notifications
- Responsive design for all screen sizes

### Data Persistence
- All messages stored in SQLite database
- Room and message data persists across server restarts
- Automatic cleanup on room deletion

## Security Considerations

For production deployment, consider:
- Authentication/authorization system
- Rate limiting for API endpoints
- Input validation and sanitization
- HTTPS/WSS encryption
- CORS configuration
- SQL injection prevention (already implemented via parameterized queries)

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Database Locked Error
If you encounter database locked errors:
- Ensure only one server instance is running
- Close any database browsers
- Delete `chat.db` and restart

### WebSocket Connection Failed
- Ensure the backend server is running
- Check browser console for errors
- Verify firewall settings allow WebSocket connections

## Future Enhancements

Potential improvements:
- User authentication
- Private direct messages
- File/image sharing
- Message reactions/emojis
- Message editing/deletion
- Read receipts
- User profiles and avatars
- Room permissions and moderation
- Message search functionality
- Pagination for large message histories

## License

This project is provided as-is for educational purposes.

## Author

Created as a demonstration of full-stack real-time web application development with FastAPI and WebSockets.
