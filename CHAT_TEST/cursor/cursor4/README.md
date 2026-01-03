# Real-time Chat System

A full-stack real-time chat application built with FastAPI (WebSockets) and vanilla JavaScript. Features multiple chat rooms, real-time messaging, typing indicators, and persistent message storage.

## Features

### Backend
- **REST API** for room and message management
- **WebSocket** connections for real-time communication
- **SQLite** database for persistent storage
- **Room management** - create, list, and delete chat rooms
- **Message history** - retrieve past messages when joining a room
- **Connection management** - handle multiple concurrent users
- **Broadcasting** - real-time message delivery to all room participants

### Frontend
- **Modern UI** - Clean, responsive design with gradient styling
- **Real-time messaging** - Instant message delivery via WebSockets
- **Online users** - See who's currently in the chat room
- **Typing indicators** - Know when others are typing
- **Connection status** - Visual feedback on connection state
- **Reconnection logic** - Automatic reconnection with exponential backoff
- **Message history** - View past messages when joining a room

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── routes.py               # API routes and WebSocket endpoint
│   └── connection_manager.py   # WebSocket connection management
├── frontend/
│   ├── index.html              # Main HTML page
│   ├── style.css               # Styling
│   └── app.js                  # JavaScript application logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   └── test_chat.py            # Comprehensive test suite (12 tests)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

1. **Clone the repository** (or ensure you're in the project directory)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Start the Backend Server

From the project root directory:

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Access the Frontend

Open your web browser and navigate to:
```
http://localhost:8000
```

The frontend is automatically served by FastAPI's StaticFiles.

## API Documentation

Once the server is running, visit:
- **Interactive API docs (Swagger UI):** `http://localhost:8000/docs`
- **Alternative API docs (ReDoc):** `http://localhost:8000/redoc`

### REST API Endpoints

#### Create a Room
```http
POST /api/chat/rooms
Content-Type: application/json

{
  "name": "General Chat"
}
```

#### List All Rooms
```http
GET /api/chat/rooms
```

#### Get Room Messages
```http
GET /api/chat/rooms/{room_id}/messages
```

#### Delete a Room
```http
DELETE /api/chat/rooms/{room_id}
```

### WebSocket Endpoint

```
ws://localhost:8000/ws/chat/{room_id}?username={username}
```

**Message Types:**
- `message` - Chat message
- `typing` - Typing indicator
- `join` - User joined notification
- `leave` - User left notification
- `users_list` - Current online users

**Example WebSocket Message:**
```json
{
  "type": "message",
  "content": "Hello, world!"
}
```

## Running Tests

The project includes a comprehensive test suite with 12 tests covering:
- REST API endpoints (room creation, listing, deletion)
- Message history retrieval
- WebSocket connections
- Message broadcasting
- Typing indicators
- Connection handling
- Data persistence

**Run all tests:**
```bash
pytest tests/ -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=backend --cov-report=html
```

**Test Categories:**
1. `test_create_room` - Room creation via REST API
2. `test_create_duplicate_room` - Duplicate room error handling
3. `test_list_rooms` - Listing all rooms
4. `test_get_room_messages` - Message history retrieval
5. `test_delete_room` - Room deletion with cascade
6. `test_delete_nonexistent_room` - Error handling for invalid room
7. `test_websocket_connection` - WebSocket connection and join
8. `test_websocket_message_broadcasting` - Multi-user message broadcast
9. `test_websocket_typing_indicator` - Typing indicator functionality
10. `test_websocket_invalid_room` - Connection to non-existent room
11. `test_websocket_leave_notification` - User disconnect notifications
12. `test_message_persistence` - Database persistence verification

## Usage Guide

### 1. Set Your Username
When you first open the app, enter your username and click "Continue".

### 2. Create or Join a Room
- **Create a new room:** Enter a room name and click "Create Room"
- **Join existing room:** Click on any room in the list

### 3. Chat in Real-time
- Type your message in the input field at the bottom
- Press Enter or click "Send" to send the message
- Messages appear in real-time for all connected users
- See typing indicators when others are composing messages

### 4. View Online Users
The sidebar shows all users currently connected to the room.

### 5. Leave a Room
Click the "Back" button to return to the room selection screen.

### 6. Delete a Room
Click the "Delete" button next to any room in the room list (this will disconnect all users).

## Technical Details

### Database Schema

**Rooms Table:**
- `id` - Primary key
- `name` - Unique room name
- `created_at` - Timestamp

**Messages Table:**
- `id` - Primary key
- `room_id` - Foreign key to rooms
- `username` - Message sender
- `content` - Message text
- `timestamp` - Message time

### WebSocket Connection Management

The `ConnectionManager` class handles:
- Multiple concurrent WebSocket connections
- Room-based message routing
- User presence tracking
- Graceful disconnection handling
- Failed connection cleanup

### Frontend Architecture

The frontend is built with vanilla JavaScript using a class-based architecture:
- `ChatApp` class manages application state
- Screen-based navigation (login → rooms → chat)
- WebSocket connection with automatic reconnection
- Graceful error handling and user feedback

## Error Handling

### Backend
- Duplicate room names return 400 Bad Request
- Non-existent rooms return 404 Not Found
- WebSocket connections to invalid rooms close with code 4004
- Database errors are logged and return appropriate HTTP status codes

### Frontend
- Connection failures trigger automatic reconnection (up to 5 attempts)
- Visual connection status indicator
- User-friendly error messages
- Input validation before sending

## Browser Compatibility

The application works in all modern browsers that support:
- WebSocket API
- ES6 JavaScript
- CSS Grid and Flexbox
- Fetch API

Tested on:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Development

### Adding New Features

1. **Backend:** Add routes in `routes.py`, models in `models.py`, schemas in `schemas.py`
2. **Frontend:** Extend the `ChatApp` class in `app.js`
3. **Tests:** Add test cases in `tests/test_chat.py`

### Database Migrations

Currently using SQLAlchemy with automatic table creation. For production, consider using Alembic for migrations.

### Environment Variables

For production deployment, configure:
- `DATABASE_URL` - Database connection string
- `CORS_ORIGINS` - Allowed CORS origins
- `SECRET_KEY` - For authentication (if added)

## Security Considerations

This is a demo application. For production use, consider adding:
- User authentication and authorization
- Rate limiting
- Input sanitization (currently basic HTML escaping)
- HTTPS/WSS encryption
- CSRF protection
- Session management
- Message content moderation

## Performance

- SQLite is suitable for development and small deployments
- For production, consider PostgreSQL or MySQL
- WebSocket connections are lightweight (< 1KB per connection)
- Messages are broadcast only to relevant room participants

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

This is a demo project. Feel free to fork and modify as needed.

## Troubleshooting

### "Failed to connect to WebSocket"
- Ensure the backend server is running
- Check that you're using the correct port (default: 8000)
- Verify firewall settings allow WebSocket connections

### "Room not found" error
- The room may have been deleted
- Refresh the page to reload the room list

### Messages not appearing
- Check your internet connection
- Look at the connection status indicator (top right)
- Try refreshing the page

### Tests failing
- Ensure you're running tests from the project root directory
- Check that all dependencies are installed
- Verify no other instance of the app is running on the same port

## Future Enhancements

Possible improvements:
- Private messaging
- File/image sharing
- Message editing and deletion
- User profiles with avatars
- Message reactions (emoji)
- Message search functionality
- Room permissions and moderation
- Voice/video chat integration
- Mobile app versions
- Message encryption

## Contact

For questions or issues, please refer to the project documentation or create an issue in the repository.


