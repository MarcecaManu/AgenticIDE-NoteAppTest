# Real-time Chat System

A full-stack real-time chat application built with FastAPI (WebSockets) and vanilla JavaScript.

## Features

### Backend (FastAPI + WebSockets)
- **REST API** for room and message management
- **WebSocket** endpoint for real-time messaging
- **Persistent storage** using SQLAlchemy with SQLite
- **Connection management** with automatic reconnection handling
- **Broadcasting** to all users in a room
- **Typing indicators** to show when users are typing
- **Join/leave notifications** for room awareness

### Frontend (HTML + JavaScript)
- **Room management**: Create and join chat rooms
- **Real-time messaging**: Send and receive messages instantly
- **Online users**: See who's currently in the room
- **Message history**: View past messages when joining a room
- **Connection handling**: Graceful handling of connection failures with auto-reconnect
- **Typing indicators**: See when others are typing
- **Responsive design**: Works on desktop and mobile

### Tests
- 16 comprehensive automated tests covering:
  - REST API endpoints
  - WebSocket connections
  - Message broadcasting
  - Room management
  - Connection handling
  - Typing indicators
  - Data persistence

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── database.py             # Database models and configuration
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── connection_manager.py  # WebSocket connection management
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html             # Main HTML file
│   ├── styles.css             # CSS styling
│   └── app.js                 # JavaScript application logic
└── tests/
    └── test_chat_system.py    # Automated tests
```

## API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/rooms` | Create a new chat room |
| GET | `/api/chat/rooms` | List all chat rooms |
| GET | `/api/chat/rooms/{room_id}/messages` | Get message history |
| DELETE | `/api/chat/rooms/{room_id}` | Delete a room and its messages |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| WS | `/ws/chat/{room_id}?username={username}` | Connect to a chat room |

#### WebSocket Message Types

**Client → Server:**
```json
// Send a message
{
  "type": "message",
  "content": "Hello, world!"
}

// Typing indicator
{
  "type": "typing",
  "is_typing": true
}
```

**Server → Client:**
```json
// New message
{
  "type": "message",
  "id": 1,
  "username": "John",
  "content": "Hello!",
  "timestamp": "2026-01-02T12:00:00"
}

// User joined
{
  "type": "join",
  "username": "Alice",
  "content": "Alice joined the room",
  "timestamp": "2026-01-02T12:00:00"
}

// User left
{
  "type": "leave",
  "username": "Bob",
  "content": "Bob left the room",
  "timestamp": "2026-01-02T12:00:00"
}

// Online users list
{
  "type": "user_list",
  "users": ["Alice", "John"],
  "timestamp": "2026-01-02T12:00:00"
}

// Typing indicators
{
  "type": "typing",
  "users": ["Alice"],
  "timestamp": "2026-01-02T12:00:00"
}
```

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the frontend files using any static file server. For example:

**Using Python:**
```bash
python -m http.server 3000
```

**Using Node.js (http-server):**
```bash
npx http-server -p 3000
```

The frontend will be available at `http://localhost:3000`

### Running Tests

1. Navigate to the backend directory:
```bash
cd backend
```

2. Run the tests:
```bash
pytest ../tests/test_chat_system.py -v
```

Or from the project root:
```bash
cd tests
pytest test_chat_system.py -v
```

## Usage

1. **Start the backend server** (see Backend Setup above)

2. **Open the frontend** in your web browser

3. **Enter your username** on the welcome screen

4. **Create a new room** or **join an existing room**

5. **Start chatting!** Messages are sent in real-time to all users in the room

### Features to Try

- **Multiple users**: Open the app in multiple browser tabs with different usernames
- **Room switching**: Leave a room and join another
- **Typing indicators**: Start typing to see the typing indicator
- **Connection resilience**: The app will automatically try to reconnect if the connection is lost
- **Message history**: Leave and rejoin a room to see message history

## Database

The application uses SQLite for data persistence. The database file (`chat.db`) is created automatically in the backend directory when you first run the server.

### Database Schema

**rooms**
- id (Primary Key)
- name (Unique)
- created_at

**messages**
- id (Primary Key)
- room_id (Foreign Key → rooms.id)
- username
- content
- timestamp

## Development

### Adding New Features

The codebase is modular and easy to extend:

- **Add new REST endpoints**: Edit `backend/main.py`
- **Modify database models**: Edit `backend/database.py`
- **Update WebSocket logic**: Edit `backend/connection_manager.py`
- **Change UI**: Edit `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`
- **Add tests**: Edit `tests/test_chat_system.py`

### API Documentation

When the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

## Troubleshooting

### Backend won't start
- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`
- Check if port 8000 is available
- Look for error messages in the console

### Frontend can't connect to backend
- Verify the backend is running at `http://localhost:8000`
- Check the `API_BASE` and `WS_BASE` constants in `frontend/app.js`
- Ensure CORS is enabled (already configured in the backend)

### Tests fail
- Ensure you're in the correct directory
- Delete `test.db` if it exists and try again
- Check that all backend dependencies are installed

### WebSocket connection issues
- Check browser console for errors
- Verify the room exists before connecting
- Ensure your firewall isn't blocking WebSocket connections

## License

This project is provided as-is for educational purposes.

## Contributing

Feel free to submit issues and enhancement requests!
