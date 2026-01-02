# System Architecture

## Overview

This is a full-stack real-time chat system built with modern web technologies, featuring persistent storage, WebSocket communication, and a clean separation of concerns.

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework with automatic API documentation
- **WebSockets**: Full-duplex communication for real-time messaging
- **SQLite**: Lightweight, file-based database for persistent storage
- **Pydantic**: Data validation and settings management
- **Uvicorn**: Lightning-fast ASGI server

### Frontend
- **Vanilla JavaScript**: No framework dependencies, pure ES6+
- **HTML5**: Semantic markup with modern standards
- **CSS3**: Responsive design with flexbox and grid
- **WebSocket API**: Native browser WebSocket support

### Testing
- **Pytest**: Python testing framework
- **TestClient**: FastAPI's built-in test client for API testing
- **WebSocket Testing**: Full WebSocket connection testing

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  index.html │  │  styles.css  │  │    app.js    │       │
│  │   (View)    │  │  (Styling)   │  │ (Controller) │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                           │
                    HTTP / WebSocket
                           │
┌─────────────────────────────────────────────────────────────┐
│                        Backend Layer                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    main.py (FastAPI)                  │   │
│  │  ┌─────────────┐              ┌──────────────────┐  │   │
│  │  │ REST API    │              │ WebSocket Server │  │   │
│  │  │ Endpoints   │              │ (ConnectionMgr)  │  │   │
│  │  └─────────────┘              └──────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    models.py                          │   │
│  │         (Pydantic Models for Validation)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   database.py                         │   │
│  │         (Data Access Layer + SQLite)                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           │
                      SQL Queries
                           │
                    ┌──────────────┐
                    │   chat.db    │
                    │   (SQLite)   │
                    └──────────────┘
```

## Component Details

### Backend Components

#### 1. main.py - Application Entry Point
**Responsibilities:**
- FastAPI application initialization
- CORS middleware configuration
- REST API route handlers
- WebSocket endpoint management
- Connection manager orchestration

**Key Classes:**
- `ConnectionManager`: Manages WebSocket connections per room

**REST Endpoints:**
- `POST /api/chat/rooms` - Create room
- `GET /api/chat/rooms` - List rooms
- `GET /api/chat/rooms/{room_id}/messages` - Get messages
- `DELETE /api/chat/rooms/{room_id}` - Delete room

**WebSocket Endpoint:**
- `WS /ws/chat/{room_id}?username={username}` - Real-time chat

#### 2. database.py - Data Persistence Layer
**Responsibilities:**
- SQLite database initialization
- CRUD operations for rooms and messages
- Connection management with context managers
- Database schema maintenance

**Key Functions:**
- `init_db()`: Creates tables and indexes
- `get_db()`: Context manager for connections
- `ChatDatabase`: Static methods for data operations

**Database Schema:**
```sql
rooms (id, name, created_at)
messages (id, room_id, username, content, timestamp)
```

#### 3. models.py - Data Validation
**Responsibilities:**
- Request/response validation
- Type safety with Pydantic
- Data serialization/deserialization

**Models:**
- `RoomCreate`: Room creation request
- `Room`: Room response
- `Message`: Message response
- `WebSocketMessage`: WebSocket message format

### Frontend Components

#### 1. index.html - User Interface
**Structure:**
- Login screen
- Room selection screen
- Chat interface with sidebar

**Features:**
- Semantic HTML5 markup
- Accessible form controls
- Mobile-responsive layout

#### 2. styles.css - Styling
**Design:**
- Modern gradient background
- Card-based UI components
- Flexbox/Grid layouts
- Responsive breakpoints
- Custom scrollbar styling

**Theme:**
- Primary color: #667eea (purple-blue)
- Success: #28a745 (green)
- Danger: #dc3545 (red)

#### 3. app.js - Client Logic
**Responsibilities:**
- State management
- WebSocket connection handling
- REST API calls
- UI updates and rendering
- Event handling

**Key Functions:**
- `connectWebSocket()`: Establishes WebSocket connection
- `handleWebSocketMessage()`: Processes incoming messages
- `renderMessages()`: Updates message display
- `loadRooms()`: Fetches room list from API

**State Management:**
```javascript
state = {
    username: null,
    currentRoom: null,
    websocket: null,
    rooms: [],
    messages: [],
    users: []
}
```

## Data Flow

### Creating a Room
```
User Input → POST /api/chat/rooms → ChatDatabase.create_room() 
→ SQLite INSERT → Return room object → Update UI
```

### Sending a Message
```
User Input → WebSocket.send({type: 'message', content: '...'})
→ ConnectionManager.broadcast() → All connected clients
→ ChatDatabase.create_message() → SQLite INSERT
```

### Joining a Room
```
Load history: GET /api/chat/rooms/{room_id}/messages
→ ChatDatabase.get_room_messages() → Render messages

Connect WebSocket: WS /ws/chat/{room_id}
→ ConnectionManager.connect() → Broadcast join notification
→ Send user list to all clients
```

## WebSocket Message Protocol

### Client → Server
```json
{"type": "message", "content": "text"}
{"type": "typing"}
```

### Server → Client
```json
{"type": "message", "message": {...}}
{"type": "join", "username": "alice", "timestamp": "..."}
{"type": "leave", "username": "bob", "timestamp": "..."}
{"type": "user_list", "users": ["alice", "bob"]}
{"type": "typing", "username": "alice", "timestamp": "..."}
{"type": "room_deleted", "message": "..."}
```

## Connection Management

### WebSocket Lifecycle
1. **Connection**: Client connects with username and room_id
2. **Validation**: Server validates room exists and username provided
3. **Registration**: Connection added to ConnectionManager
4. **Join Broadcast**: Server notifies all users of new join
5. **User List**: Updated user list sent to all clients
6. **Active Session**: Message exchange, typing indicators
7. **Disconnection**: Server detects disconnect
8. **Leave Broadcast**: Server notifies all users of leave
9. **Cleanup**: Connection removed from ConnectionManager

### Reconnection Strategy
- Client detects disconnect (onclose event)
- Wait 3 seconds
- Attempt reconnection if still on chat screen
- Repeat until successful or user leaves room

## Security Considerations

### Input Validation
- Pydantic models validate all input
- Length limits on usernames (50) and messages (1000)
- HTML escaping on frontend to prevent XSS
- SQL injection prevented by parameterized queries

### Connection Security
- Username required for WebSocket connection
- Room existence validated before connection
- CORS configured (customize for production)

### Data Integrity
- Foreign key constraints ensure referential integrity
- CASCADE delete removes messages when room deleted
- Transactions ensure atomic operations

## Performance Optimizations

### Database
- Indexes on `room_id` and `timestamp` for fast queries
- Connection pooling via context managers
- Limit queries to prevent excessive data transfer

### WebSocket
- Efficient broadcast mechanism
- Disconnected user cleanup
- Per-room connection isolation

### Frontend
- Minimal DOM updates
- Event delegation
- Debounced typing indicators (1 second)
- Scroll optimization

## Testing Strategy

### Unit Tests
- Database operations (CRUD)
- Model validation
- Connection manager logic

### Integration Tests
- REST API endpoints
- WebSocket connections
- Message broadcasting
- User management

### Coverage
- Room creation/deletion
- Message sending/receiving
- Join/leave notifications
- Typing indicators
- Connection validation
- Error handling

## Deployment Considerations

### Backend
- Use Gunicorn/Uvicorn workers for production
- Configure CORS for specific origins
- Use PostgreSQL for production (optional)
- Set up reverse proxy (Nginx)
- Enable HTTPS for secure WebSockets (WSS)

### Frontend
- Serve via CDN or static hosting
- Update API/WS URLs for production
- Enable compression (gzip/brotli)
- Cache static assets

### Database
- Regular backups for SQLite
- Consider PostgreSQL for scale
- Monitor connection pool
- Implement data retention policy

## Scalability Path

### Current Limitations
- Single server (no horizontal scaling)
- SQLite (single writer)
- In-memory connection tracking

### Scaling Solutions
1. **Redis**: For distributed connection tracking
2. **PostgreSQL**: For concurrent writes and replication
3. **Message Queue**: RabbitMQ/Redis for message distribution
4. **Load Balancer**: Nginx with sticky sessions
5. **Microservices**: Separate chat, storage, and auth services

## Future Enhancements

### Features
- User authentication (JWT)
- Private messaging
- File/image sharing
- Message reactions
- User profiles
- Message search
- Read receipts
- Message editing/deletion

### Technical
- Database migrations (Alembic)
- Caching layer (Redis)
- Rate limiting
- Monitoring/logging
- CI/CD pipeline
- Docker containerization

## Development Guidelines

### Code Style
- PEP 8 for Python
- ESLint for JavaScript (optional)
- Type hints for Python
- JSDoc comments for JavaScript

### Git Workflow
- Feature branches
- Pull request reviews
- Semantic versioning
- Comprehensive commit messages

### Documentation
- Inline comments for complex logic
- API documentation (FastAPI auto-docs)
- Architecture updates as system evolves
- README maintenance

---

**Last Updated**: January 2026  
**Version**: 1.0.0

