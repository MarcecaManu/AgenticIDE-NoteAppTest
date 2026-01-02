# Real-time Chat System

A full-stack real-time chat application built with FastAPI (backend) and vanilla HTML/CSS/JavaScript (frontend). Features WebSocket-based real-time messaging, room management, typing indicators, and persistent message storage.

## Features

### Backend
- **REST API** for room and message management
- **WebSocket** support for real-time messaging
- **Persistent storage** using SQLite with async support
- **Room management** - create, list, and delete chat rooms
- **Message history** - retrieve past messages when joining a room
- **Connection handling** - join/leave notifications and user tracking

### Frontend
- **Real-time messaging** - send and receive messages instantly
- **Room management** - create and join chat rooms
- **Online users** - see who's currently in the room
- **Typing indicators** - see when others are typing
- **Message history** - view past messages when joining
- **Connection status** - visual feedback for connection state
- **Auto-reconnect** - automatic reconnection on connection loss

### Testing
- Comprehensive test suite with 13+ tests
- REST API endpoint testing
- WebSocket connection testing
- Message broadcasting verification
- Room management testing
- Connection handling tests

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── database.py             # Database operations and models
│   ├── models.py               # Pydantic models for validation
│   ├── websocket_manager.py    # WebSocket connection management
│   └── requirements.txt        # Backend dependencies
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── styles.css              # Styling
│   └── chat.js                 # Frontend JavaScript logic
├── tests/
│   ├── conftest.py             # Test configuration and fixtures
│   ├── test_rest_api.py        # REST API tests
│   ├── test_websocket.py       # WebSocket tests
│   └── requirements.txt        # Test dependencies
└── README.md
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project**
   ```bash
   cd cursor2
   ```

2. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

3. **Install test dependencies (optional)**
   ```bash
   cd tests
   pip install -r requirements.txt
   cd ..
   ```

## Running the Application

### Start the Backend Server

From the project root directory:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

### Access the Frontend

Open your web browser and navigate to:
```
http://localhost:8000
```

The frontend is automatically served by the FastAPI backend.

## API Documentation

### REST API Endpoints

#### Create a Room
```http
POST /api/chat/rooms
Content-Type: application/json

{
  "name": "My Chat Room"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid-string",
  "name": "My Chat Room",
  "created_at": "2024-01-01T12:00:00.000000"
}
```

#### Get All Rooms
```http
GET /api/chat/rooms
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid-string",
    "name": "Room 1",
    "created_at": "2024-01-01T12:00:00.000000"
  },
  ...
]
```

#### Get Room Messages
```http
GET /api/chat/rooms/{room_id}/messages?limit=100
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid-string",
    "room_id": "room-uuid",
    "username": "John",
    "content": "Hello!",
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  ...
]
```

#### Delete a Room
```http
DELETE /api/chat/rooms/{room_id}
```

**Response (204 No Content)**

### WebSocket Endpoint

#### Connect to a Room
```
ws://localhost:8000/ws/chat/{room_id}?username={username}
```

#### Message Types

**Send a Message:**
```json
{
  "type": "message",
  "content": "Hello, everyone!"
}
```

**Typing Indicator:**
```json
{
  "type": "typing",
  "is_typing": true
}
```

**Request User List:**
```json
{
  "type": "get_users"
}
```

**Received Messages:**

Message received:
```json
{
  "type": "message",
  "data": {
    "id": "uuid",
    "room_id": "room-uuid",
    "username": "John",
    "content": "Hello!",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

User joined:
```json
{
  "type": "join",
  "data": {
    "username": "Jane",
    "message": "Jane joined the room"
  }
}
```

User left:
```json
{
  "type": "leave",
  "data": {
    "username": "Jane",
    "message": "Jane left the room"
  }
}
```

User list:
```json
{
  "type": "user_list",
  "data": {
    "users": ["John", "Jane", "Bob"]
  }
}
```

Typing indicator:
```json
{
  "type": "typing",
  "data": {
    "username": "John",
    "is_typing": true
  }
}
```

## Running Tests

Make sure you're in the project root directory and have installed test dependencies:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_rest_api.py -v
pytest tests/test_websocket.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html
```

### Test Coverage

The test suite includes:
- **7 REST API tests**: room creation, retrieval, deletion, message history
- **6 WebSocket tests**: connections, message broadcasting, typing indicators, join/leave notifications, message persistence

## Usage Guide

### Creating and Joining a Room

1. Enter your username
2. Either:
   - Select an existing room from the list
   - Create a new room by entering a name and clicking "Create Room"
3. Click "Join Room"

### Chatting

1. Type your message in the input field at the bottom
2. Press Enter or click "Send" to send the message
3. Your message will appear for all users in the room instantly

### Features in Chat

- **Online Users**: See who's currently in the room (left sidebar)
- **Typing Indicators**: See when others are typing
- **Connection Status**: Monitor your connection state (bottom of sidebar)
- **Message History**: Scroll up to see previous messages
- **Leave Room**: Click "Leave" to return to the room selection screen

## Technical Details

### Backend Technologies
- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **SQLite + aiosqlite**: Async database for persistent storage
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running the application

### Frontend Technologies
- **Vanilla JavaScript**: No frameworks, just pure JS
- **WebSocket API**: Browser's native WebSocket support
- **CSS Grid/Flexbox**: Modern responsive layout
- **Async/Await**: Modern JavaScript async patterns

### Database Schema

**Rooms Table:**
```sql
CREATE TABLE rooms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
)
```

**Messages Table:**
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

## Features Explained

### Connection Management
- Automatic reconnection with exponential backoff
- Visual connection status indicator
- Graceful handling of connection failures
- Maximum 5 reconnection attempts

### Message Broadcasting
- Messages are broadcast to all connected users in the same room
- Sender also receives their own message for confirmation
- Messages are persisted before broadcasting

### Typing Indicators
- Shows when a user is typing
- Automatically clears after 2 seconds of inactivity
- Users don't see their own typing indicator

### User Presence
- Join/leave notifications for all room members
- Real-time user list updates
- User count display

## Development

### Adding New Features

1. **Backend**: Add endpoints in `backend/main.py`, database operations in `backend/database.py`
2. **Frontend**: Modify `frontend/chat.js` for logic, `frontend/styles.css` for styling
3. **Tests**: Add tests in `tests/` directory

### Code Organization

- **Models**: Data validation and type definitions in `backend/models.py`
- **Database**: All database operations in `backend/database.py`
- **WebSocket**: Connection management in `backend/websocket_manager.py`
- **API**: REST and WebSocket endpoints in `backend/main.py`
- **Frontend**: Separated into HTML structure, CSS styling, and JS logic

## Troubleshooting

### Cannot connect to server
- Ensure the backend server is running on port 8000
- Check if another application is using port 8000

### WebSocket connection fails
- Verify the room exists before connecting
- Check browser console for error messages
- Ensure firewall allows WebSocket connections

### Messages not appearing
- Check connection status indicator
- Verify WebSocket connection is active
- Look for errors in browser console

### Tests failing
- Ensure backend dependencies are installed
- Delete `backend/chat.db` if it exists
- Run tests from project root directory

## Security Notes

This is a demonstration application. For production use, consider adding:
- User authentication and authorization
- Message encryption
- Rate limiting
- Input sanitization (already implemented with HTML escaping)
- CSRF protection
- SQL injection prevention (using parameterized queries)
- XSS prevention (HTML escaping implemented)

## License

This project is provided as-is for educational and demonstration purposes.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation
3. Check test files for usage examples

