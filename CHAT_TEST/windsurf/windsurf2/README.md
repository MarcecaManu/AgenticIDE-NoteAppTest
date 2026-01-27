# Real-time Chat System

A full-stack real-time chat application built with FastAPI WebSockets backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI)
- **REST API** at `/api/chat/` for chat history and room management
- **WebSocket** endpoint at `/ws/chat/{room_id}` for real-time messaging
- **Persistent storage** using SQLite for rooms and messages
- **Real-time features**: join/leave notifications, message broadcasting, typing indicators
- **Connection management**: handles multiple users per room, graceful disconnections

### Frontend (HTML/JavaScript)
- **Modern UI** with gradient design and smooth animations
- **Real-time messaging** with WebSocket connections
- **Room management**: create, join, and view chat rooms
- **Online presence**: see who's currently in the room
- **Message history**: load previous messages when joining
- **Typing indicators**: see when others are typing
- **Connection status**: visual feedback for connection state
- **Auto-reconnection**: automatically reconnects on connection loss

### REST API Endpoints

#### POST /api/chat/rooms
Create a new chat room.

**Request:**
```json
{
  "name": "My Chat Room"
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "name": "My Chat Room",
  "created_at": "2024-01-24T10:00:00Z"
}
```

#### GET /api/chat/rooms
List all chat rooms.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "name": "My Chat Room",
    "created_at": "2024-01-24T10:00:00Z"
  }
]
```

#### GET /api/chat/rooms/{room_id}/messages
Get message history for a room.

**Response:**
```json
[
  {
    "id": 1,
    "room_id": "uuid-string",
    "username": "Alice",
    "content": "Hello!",
    "timestamp": "2024-01-24T10:00:00Z"
  }
]
```

#### DELETE /api/chat/rooms/{room_id}
Delete a room and all its messages.

**Response:**
```json
{
  "message": "Room deleted successfully"
}
```

### WebSocket Protocol

Connect to: `ws://localhost:8000/ws/chat/{room_id}?username={username}`

#### Client → Server Messages

**Send a message:**
```json
{
  "type": "message",
  "content": "Hello everyone!"
}
```

**Send typing indicator:**
```json
{
  "type": "typing",
  "is_typing": true
}
```

#### Server → Client Messages

**User joined:**
```json
{
  "type": "user_joined",
  "username": "Alice",
  "online_users": ["Alice", "Bob"],
  "timestamp": "2024-01-24T10:00:00Z"
}
```

**User left:**
```json
{
  "type": "user_left",
  "username": "Bob",
  "online_users": ["Alice"],
  "timestamp": "2024-01-24T10:00:00Z"
}
```

**New message:**
```json
{
  "type": "message",
  "id": 1,
  "room_id": "uuid-string",
  "username": "Alice",
  "content": "Hello!",
  "timestamp": "2024-01-24T10:00:00Z"
}
```

**Typing indicator:**
```json
{
  "type": "typing",
  "username": "Bob",
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
│   ├── index.html          # Main HTML page
│   └── app.js              # JavaScript client logic
├── tests/
│   ├── test_chat.py        # Comprehensive test suite
│   └── requirements.txt    # Test dependencies
└── README.md               # This file
```

## Installation & Setup

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

2. Serve the files using any HTTP server. For example, with Python:
```bash
python -m http.server 8080
```

3. Open your browser and navigate to:
```
http://localhost:8080
```

### Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
```

3. Install backend dependencies (if not already installed):
```bash
pip install -r ../backend/requirements.txt
```

4. Run the test suite:
```bash
pytest test_chat.py -v
```

## Usage

1. **Start the backend server** (see Backend Setup above)
2. **Open the frontend** in your browser (see Frontend Setup above)
3. **Enter your username** in the sidebar
4. **Create a new room** or join an existing one
5. **Start chatting** in real-time!

## Testing

The test suite includes 14 comprehensive tests covering:

- ✅ REST endpoint functionality (create, list, get, delete rooms)
- ✅ Message retrieval and persistence
- ✅ WebSocket connections and authentication
- ✅ Real-time message broadcasting
- ✅ Multiple users in the same room
- ✅ Typing indicators
- ✅ User join/leave notifications
- ✅ Connection handling and disconnections
- ✅ Duplicate connection prevention (single connection per user)
- ✅ Error handling (room not found, etc.)

Run tests with:
```bash
cd tests
pytest test_chat.py -v
```

## Technical Details

### Backend Technologies
- **FastAPI**: Modern Python web framework
- **WebSockets**: Real-time bidirectional communication
- **SQLite**: Lightweight persistent storage
- **Pydantic**: Data validation and serialization
- **CORS**: Cross-origin resource sharing enabled

### Frontend Technologies
- **Vanilla JavaScript**: No frameworks, pure JS
- **WebSocket API**: Native browser WebSocket support
- **Fetch API**: Modern HTTP requests
- **CSS3**: Gradients, animations, flexbox layout

### Security Features
- Input sanitization (HTML escaping)
- Room validation before WebSocket connections
- Graceful error handling
- Connection status monitoring

### Data Models

**Room:**
- `id`: Unique identifier (UUID)
- `name`: Room name
- `created_at`: ISO 8601 timestamp

**Message:**
- `id`: Auto-incrementing integer
- `room_id`: Foreign key to room
- `username`: Sender's username
- `content`: Message text
- `timestamp`: ISO 8601 timestamp

## License

This project is open source and available for educational purposes.
