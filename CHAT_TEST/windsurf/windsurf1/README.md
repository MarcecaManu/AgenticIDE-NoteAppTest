# Real-time Chat System

A full-stack real-time chat application built with FastAPI WebSockets backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **REST API** at `/api/chat/` for chat history and room management
- **WebSocket endpoint** at `/ws/chat/{room_id}` for real-time messaging
- Persistent storage using JSON files
- Room management (create, list, delete)
- Message history retrieval
- Real-time message broadcasting
- User presence tracking
- Typing indicators

### Frontend (HTML/JavaScript)
- Modern, responsive UI with gradient design
- Real-time messaging with WebSocket
- Join/create chat rooms
- View online users in each room
- Typing indicators
- Message history on room join
- Connection status monitoring
- Automatic reconnection on connection loss
- Graceful error handling

### REST Endpoints

- `POST /api/chat/rooms` - Create a new chat room
- `GET /api/chat/rooms` - List all chat rooms
- `GET /api/chat/rooms/{room_id}/messages` - Get message history for a room
- `DELETE /api/chat/rooms/{room_id}` - Delete a room and its messages

### WebSocket Functionality

- Join/leave room notifications
- Real-time message broadcasting to all users in a room
- User typing indicators
- Connection status management
- Online user list updates

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application with REST and WebSocket endpoints
│   ├── requirements.txt     # Python dependencies
│   └── data/               # Persistent storage (auto-created)
│       ├── rooms.json      # Chat rooms data
│       └── messages.json   # Messages data
├── frontend/
│   ├── index.html          # Main HTML file
│   ├── styles.css          # Styling
│   └── app.js              # JavaScript logic
└── tests/
    └── test_chat.py        # Comprehensive test suite
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

3. Run the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Serve the frontend using any HTTP server. For example, using Python:
```bash
python -m http.server 3000
```

Or using Node.js:
```bash
npx http-server -p 3000
```

The frontend will be available at `http://localhost:3000`

## Running Tests

1. Navigate to the project root directory

2. Run the test suite:
```bash
pytest tests/ -v
```

The test suite includes 12 comprehensive tests covering:
- REST endpoint functionality (create, list, get, delete rooms)
- WebSocket connections and messaging
- Multi-user chat broadcasting
- Typing indicators
- Message persistence
- Room deletion with message cleanup
- Error handling (room not found scenarios)

## Usage

1. **Start the backend server** (port 8000)
2. **Open the frontend** in your browser (port 3000)
3. **Enter your username** on the login screen
4. **Create or join a chat room**
5. **Start chatting** in real-time!

## Data Persistence

All data is stored persistently in JSON files:
- `backend/data/rooms.json` - Stores chat room information
- `backend/data/messages.json` - Stores all messages

The data directory is automatically created when the backend starts.

## Message Data Structure

Each message includes:
- `id` - Unique message identifier
- `room_id` - Associated chat room ID
- `username` - Sender's username
- `content` - Message content
- `timestamp` - ISO 8601 timestamp

## Security Features

- CORS enabled for cross-origin requests
- WebSocket connection validation
- Room existence verification
- Graceful error handling
- Connection status monitoring

## Technologies Used

### Backend
- FastAPI - Modern Python web framework
- WebSockets - Real-time bidirectional communication
- Pydantic - Data validation
- Uvicorn - ASGI server

### Frontend
- HTML5
- CSS3 (with gradients and animations)
- Vanilla JavaScript
- WebSocket API

### Testing
- pytest - Testing framework
- pytest-asyncio - Async test support
- httpx - HTTP client for testing

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

The application is designed to be:
- **Modular** - Clear separation of concerns
- **Maintainable** - Clean, readable code
- **Scalable** - Easy to extend with new features
- **Testable** - Comprehensive test coverage

## Future Enhancements

Potential improvements:
- User authentication
- Private messaging
- File sharing
- Message reactions
- Database integration (PostgreSQL/MongoDB)
- Message search functionality
- User profiles and avatars
- Message editing and deletion
- Read receipts
