# Real-time Chat Application

A full-stack real-time chat system built with FastAPI (WebSockets) for the backend and plain HTML/JavaScript for the frontend.

## Features

### Backend (FastAPI + WebSockets)
- **REST API** for chat room and message management
- **WebSocket** for real-time bidirectional communication
- **Persistent storage** using SQLite with SQLAlchemy ORM
- **Connection management** with automatic reconnection handling
- **Message broadcasting** to all users in a room
- **Typing indicators** to show when users are typing
- **Join/leave notifications** when users enter or exit rooms

### Frontend (HTML + JavaScript)
- **Responsive UI** with modern design
- **Room management** - create, join, and delete chat rooms
- **Real-time messaging** with WebSocket connection
- **Online users list** showing who's currently in the room
- **Message history** loaded when joining a room
- **Connection status** indicator with automatic reconnection
- **Typing indicators** to see when others are typing
- **Username persistence** using localStorage

### Testing
- **18 automated tests** covering:
  - REST API endpoints (room creation, listing, deletion, messages)
  - WebSocket connections and disconnections
  - Message broadcasting to multiple users
  - Room management operations
  - Typing indicators
  - User list updates
  - Connection handling and error cases

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app with REST and WebSocket endpoints
│   ├── database.py             # SQLAlchemy models and database configuration
│   ├── schemas.py              # Pydantic models for request/response
│   └── connection_manager.py   # WebSocket connection manager
├── frontend/
│   ├── index.html              # Main HTML UI
│   └── chat.js                 # JavaScript client logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_api.py            # REST API tests
│   └── test_websocket.py      # WebSocket tests
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd copilot2
   ```

2. **Create and activate a virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Start the Backend Server

```bash
# From the project root directory
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Access the Frontend

Open your web browser and navigate to:
```
http://localhost:8000
```

Or open `frontend/index.html` directly in your browser (for development).

**Note**: If opening the HTML file directly, make sure to update the API URLs in `frontend/chat.js` if your backend is running on a different host/port.

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

Connect to a room:
```
ws://localhost:8000/ws/chat/{room_id}?username={username}
```

**Message Types:**

1. **Send a message**
```json
{
  "message_type": "message",
  "content": "Hello, everyone!"
}
```

2. **Typing indicator**
```json
{
  "message_type": "typing",
  "is_typing": true
}
```

## Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_api.py -v
pytest tests/test_websocket.py -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=backend --cov-report=html
```

### Test Coverage

The test suite includes 18 tests covering:
- ✅ Room creation and validation
- ✅ Room listing and deletion
- ✅ Message retrieval
- ✅ WebSocket connections
- ✅ Message broadcasting
- ✅ Multi-user scenarios
- ✅ Typing indicators
- ✅ Join/leave notifications
- ✅ Connection handling
- ✅ Error cases

## Usage Guide

### Getting Started

1. **Set your username** in the sidebar
2. **Create a new room** or select an existing one
3. **Start chatting!** Messages are sent in real-time to all users in the room

### Features Usage

- **Create Room**: Enter a room name and click "Create"
- **Join Room**: Click on any room in the list
- **Send Message**: Type your message and press Enter or click "Send"
- **Delete Room**: Click the "Delete" button next to a room name
- **View Online Users**: See the list on the right panel
- **Typing Indicator**: Start typing to show others you're composing a message

## Configuration

### Environment Variables

You can configure the database URL using environment variables:

```bash
# Use PostgreSQL instead of SQLite
export DATABASE_URL="postgresql://user:password@localhost/chatdb"

# Or MySQL
export DATABASE_URL="mysql://user:password@localhost/chatdb"
```

### CORS Settings

CORS is configured to allow all origins by default. For production, update the CORS settings in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Deployment

### Production Considerations

1. **Use a production ASGI server**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

2. **Use a production database** (PostgreSQL, MySQL) instead of SQLite

3. **Set up HTTPS/WSS** for secure connections

4. **Configure CORS** properly for your domain

5. **Add authentication** for user management

6. **Implement rate limiting** to prevent abuse

7. **Set up logging and monitoring**

## Troubleshooting

### WebSocket Connection Failed
- Ensure the backend server is running
- Check that the WebSocket URL is correct
- Verify firewall settings allow WebSocket connections

### Database Errors
- Delete `chat.db` to reset the database
- Check file permissions for the database file
- Ensure SQLAlchemy is properly installed

### Port Already in Use
- Change the port in the uvicorn command:
  ```bash
  uvicorn backend.main:app --port 8001
  ```
- Update the frontend URLs in `chat.js` accordingly

## License

This project is open source and available for educational purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Technical Details

### Technologies Used
- **Backend**: FastAPI 0.115.0, Python 3.8+
- **WebSocket**: Native FastAPI WebSocket support
- **Database**: SQLAlchemy 2.0 with SQLite
- **Testing**: pytest with async support
- **Frontend**: Vanilla JavaScript (ES6+), HTML5, CSS3

### Architecture
- **RESTful API** for CRUD operations
- **WebSocket** for real-time bidirectional communication
- **Connection Manager** pattern for WebSocket management
- **Database ORM** with relationship mapping
- **Test fixtures** for isolated test execution
