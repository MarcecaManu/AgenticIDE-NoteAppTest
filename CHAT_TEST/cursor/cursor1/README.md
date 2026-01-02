# Real-time Chat System

A full-stack real-time chat application built with FastAPI (backend) and vanilla HTML/JavaScript (frontend). Features WebSocket-based real-time messaging, persistent storage, typing indicators, and user presence tracking.

## Features

### Backend Features
- **REST API** for room and message management
- **WebSocket** real-time messaging
- **Persistent storage** using SQLite with SQLAlchemy
- **Connection management** with automatic reconnection
- **User presence tracking**
- **Typing indicators**
- **Join/leave notifications**

### Frontend Features
- **Real-time messaging** with WebSocket connection
- **Room management** (create, join, delete)
- **Message history** loaded on room join
- **Online users display**
- **Typing indicators**
- **Connection status monitoring**
- **Graceful error handling**
- **Modern, responsive UI**

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application with REST and WebSocket endpoints
│   └── models.py        # Database models and schemas
├── frontend/
│   ├── index.html       # Main HTML page
│   ├── styles.css       # Styling
│   └── app.js           # JavaScript application logic
├── tests/
│   └── test_chat_system.py  # Comprehensive test suite (10 tests)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   cd backend
   python main.py
   ```

4. **Access the application**
   - Open your browser and navigate to: `http://localhost:8000`
   - The backend API is available at: `http://localhost:8000/api/chat/`
   - API documentation (Swagger): `http://localhost:8000/docs`

## API Endpoints

### REST API

#### Create a Chat Room
```http
POST /api/chat/rooms
Content-Type: application/json

{
  "name": "Room Name",
  "description": "Optional description"
}
```

#### List All Rooms
```http
GET /api/chat/rooms
```

#### Get Room Message History
```http
GET /api/chat/rooms/{room_id}/messages?limit=100
```

#### Delete a Room
```http
DELETE /api/chat/rooms/{room_id}
```

### WebSocket

#### Connect to a Room
```
ws://localhost:8000/ws/chat/{room_id}
```

**Authentication message (sent after connection):**
```json
{
  "username": "YourUsername"
}
```

**Message types:**

**Send a message:**
```json
{
  "type": "message",
  "content": "Your message here"
}
```

**Send typing indicator:**
```json
{
  "type": "typing",
  "is_typing": true
}
```

**Received messages:**
- `connected` - Connection confirmation
- `message` - Chat message
- `system` - System notification (user joined/left)
- `users_list` - List of online users
- `typing` - Typing indicators
- `room_deleted` - Room was deleted
- `error` - Error message

## Running Tests

The project includes a comprehensive test suite with 10 automated tests covering:
- REST endpoint functionality
- WebSocket connections
- Message broadcasting
- Room management
- User presence tracking
- Typing indicators
- Connection handling
- Edge cases and error scenarios

### Run all tests:
```bash
cd tests
pytest test_chat_system.py -v
```

### Run specific test:
```bash
pytest test_chat_system.py::test_create_chat_room -v
```

### Test coverage includes:
1. ✅ Create chat room (REST API)
2. ✅ List chat rooms (REST API)
3. ✅ Get message history (REST API)
4. ✅ Delete chat room (REST API)
5. ✅ WebSocket connection and authentication
6. ✅ Message broadcasting to multiple users
7. ✅ Typing indicators
8. ✅ User join/leave notifications
9. ✅ Room deletion with active connections
10. ✅ Multiple messages in sequence

## Usage Guide

### Creating and Joining a Room

1. Click **"+ New Room"** in the sidebar
2. Enter a room name (required) and optional description
3. Click **"Create Room"**
4. Select the room from the sidebar
5. Enter your username to join

### Sending Messages

1. Type your message in the input field at the bottom
2. Press **Enter** or click **"Send"**
3. Your message will appear immediately and be broadcast to all users

### Managing Rooms

- **Delete a room**: Click the "Delete" button on any room card
- **Leave a room**: Click "Leave Room" in the chat header
- Deleting a room removes all messages and disconnects all users

### Real-time Features

- **User presence**: See who's online in the "Online Users" section
- **Typing indicators**: See when other users are typing
- **Connection status**: Monitor your connection status in the header
- **Auto-reconnect**: Automatic reconnection attempts if connection is lost

## Technical Details

### Backend Stack
- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time bidirectional communication
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database for persistence
- **Uvicorn**: ASGI server

### Frontend Stack
- **Vanilla JavaScript**: No frameworks, lightweight and fast
- **WebSocket API**: Native browser WebSocket support
- **Modern CSS**: Flexbox, CSS variables, animations
- **Responsive Design**: Works on desktop and mobile

### Database Schema

**ChatRoom Table:**
- `id`: Primary key
- `name`: Unique room name
- `description`: Optional description
- `created_at`: Timestamp

**Message Table:**
- `id`: Primary key
- `room_id`: Foreign key to ChatRoom
- `username`: Message sender
- `content`: Message text
- `timestamp`: Message time

### Connection Management

The backend maintains:
- Active WebSocket connections per room
- User lists per room
- Typing status per room
- WebSocket-to-username mapping

Features:
- Automatic cleanup on disconnect
- Room deletion notifies all connected users
- Broadcast system for efficient message distribution

## Development

### Project Architecture

The application follows a clean architecture pattern:

1. **Presentation Layer** (frontend/): HTML, CSS, JavaScript
2. **API Layer** (backend/main.py): REST and WebSocket endpoints
3. **Business Logic** (backend/main.py): ConnectionManager, message handling
4. **Data Layer** (backend/models.py): Database models and schemas
5. **Testing** (tests/): Automated test suite

### Adding New Features

**To add a new message type:**

1. Update the WebSocket handler in `backend/main.py`
2. Add message handling in `frontend/app.js`
3. Add tests in `tests/test_chat_system.py`

**To add a new REST endpoint:**

1. Add the endpoint in `backend/main.py`
2. Add corresponding frontend call in `frontend/app.js`
3. Add tests in `tests/test_chat_system.py`

## Troubleshooting

### Connection Issues
- Ensure the backend is running on port 8000
- Check browser console for WebSocket errors
- Verify firewall settings allow WebSocket connections

### Database Issues
- Delete `chat.db` to reset the database
- Check file permissions in the backend directory

### Test Failures
- Delete `test_chat.db` before running tests
- Ensure no other instance is using the test database

## Security Considerations

This is a demonstration application. For production use, consider:

- User authentication and authorization
- Input validation and sanitization
- Rate limiting
- HTTPS/WSS for encrypted connections
- CSRF protection
- Content Security Policy
- Database connection pooling
- Environment-based configuration

## License

This project is provided as-is for educational and demonstration purposes.

## Author

Built as a demonstration of full-stack real-time web application development with FastAPI and WebSockets.

