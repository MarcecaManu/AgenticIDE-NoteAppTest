# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  HTML (index.html) - Structure                         │ │
│  │  CSS (styles.css) - Modern, responsive styling         │ │
│  │  JavaScript (app.js) - Client logic & WebSocket        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
                    HTTP/REST │ WebSocket
                              │
┌─────────────────────────────┼─────────────────────────────────┐
│                      BACKEND SERVER (FastAPI)                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              main.py - Application Core                │  │
│  │                                                         │  │
│  │  ┌─────────────────┐      ┌────────────────────────┐  │  │
│  │  │  REST API       │      │ WebSocket Endpoint     │  │  │
│  │  │  /api/chat/*    │      │ /ws/chat/{room_id}     │  │  │
│  │  └─────────────────┘      └────────────────────────┘  │  │
│  │           │                          │                 │  │
│  │           │                          │                 │  │
│  │           └──────────┬───────────────┘                 │  │
│  │                      │                                 │  │
│  │           ┌──────────┴──────────┐                      │  │
│  │           │ Connection Manager  │                      │  │
│  │           │ - Active connections│                      │  │
│  │           │ - User tracking     │                      │  │
│  │           │ - Broadcasting      │                      │  │
│  │           └─────────────────────┘                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                              │                                │
│  ┌────────────────────────────────────────────────────────┐  │
│  │           models.py - Database Layer                   │  │
│  │  - SQLAlchemy ORM                                      │  │
│  │  - Pydantic schemas                                    │  │
│  │  - Database session management                         │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────┼───────────────────────────────────┘
                            │
                    ┌───────┴────────┐
                    │   SQLite DB    │
                    │  - chat_rooms  │
                    │  - messages    │
                    └────────────────┘
```

## Request Flow

### REST API Flow (Room Creation)

```
1. Client (Browser)
   └─> POST /api/chat/rooms
       { "name": "General", "description": "General chat" }

2. FastAPI Backend
   └─> Validate request (Pydantic)
   └─> Check for duplicate names
   └─> Create ChatRoom model
   └─> Save to database (SQLAlchemy)
   └─> Return response

3. Database
   └─> INSERT INTO chat_rooms (name, description, created_at)
   └─> Return new room with ID

4. Client receives
   └─> { "id": 1, "name": "General", ... }
   └─> Update UI with new room
```

### WebSocket Flow (Real-time Messaging)

```
1. Client Connection
   └─> WebSocket connect to ws://localhost:8000/ws/chat/1
   └─> Send auth: { "username": "Alice" }

2. Server (ConnectionManager)
   └─> Accept connection
   └─> Verify room exists (database)
   └─> Add connection to active_connections[room_id]
   └─> Add user to room_users[room_id]
   └─> Broadcast "Alice joined" to other users
   └─> Send users_list to all

3. Message Sending
   Client (Alice)
   └─> Send: { "type": "message", "content": "Hello!" }

4. Server Processing
   └─> Receive message from Alice's WebSocket
   └─> Save to database (Message model)
   └─> Broadcast to all connections in room
       ├─> Alice's connection (confirmation)
       ├─> Bob's connection (new message)
       └─> Carol's connection (new message)

5. Clients Receive
   └─> All connected users see message instantly
   └─> Update UI with new message
```

### Typing Indicator Flow

```
1. Client (Alice) starts typing
   └─> Send: { "type": "typing", "is_typing": true }

2. Server
   └─> Add "Alice" to typing_users[room_id]
   └─> Broadcast typing status to all users

3. All clients receive
   └─> { "type": "typing", "users": ["Alice"] }
   └─> Show "Alice is typing..."

4. After 1 second of no typing
   └─> Client sends: { "type": "typing", "is_typing": false }
   └─> Server removes "Alice" from typing_users
   └─> Broadcast updated typing status
```

## Component Architecture

### Backend Components

```
main.py
├─ FastAPI App
│  ├─ CORS Middleware
│  ├─ Static Files (frontend)
│  └─ Root endpoint (/)
│
├─ REST Endpoints
│  ├─ create_room()
│  ├─ list_rooms()
│  ├─ get_room_messages()
│  └─ delete_room()
│
├─ WebSocket Endpoint
│  └─ websocket_endpoint()
│     ├─ Authentication
│     ├─ Message handling
│     ├─ Typing indicators
│     └─ Disconnect handling
│
└─ ConnectionManager
   ├─ State Management
   │  ├─ active_connections: Dict[room_id, Set[WebSocket]]
   │  ├─ room_users: Dict[room_id, Set[username]]
   │  ├─ connection_usernames: Dict[WebSocket, username]
   │  └─ typing_users: Dict[room_id, Set[username]]
   │
   └─ Methods
      ├─ connect()
      ├─ disconnect()
      ├─ broadcast_message()
      ├─ broadcast_system_message()
      ├─ broadcast_users_list()
      ├─ broadcast_typing_status()
      └─ set_typing()

models.py
├─ SQLAlchemy Models
│  ├─ ChatRoom
│  └─ Message
│
├─ Pydantic Schemas
│  ├─ RoomCreate
│  ├─ ChatRoom (response)
│  ├─ MessageCreate
│  └─ Message (response)
│
└─ Database Utilities
   ├─ init_db()
   └─ get_db_session()
```

### Frontend Components

```
index.html
├─ Header
│  ├─ Title
│  └─ Connection Status
│
├─ Sidebar
│  ├─ Create Room Button
│  └─ Rooms List
│
├─ Main Content
│  ├─ Welcome Screen (initial)
│  └─ Chat Screen
│     ├─ Chat Header
│     ├─ Users Panel
│     ├─ Messages Container
│     └─ Message Input
│
└─ Modals
   ├─ Create Room Modal
   └─ Join Room Modal

app.js
├─ State Management
│  ├─ ws (WebSocket)
│  ├─ currentRoom
│  ├─ username
│  ├─ rooms[]
│  ├─ messages[]
│  └─ users[]
│
├─ Room Management
│  ├─ loadRooms()
│  ├─ renderRooms()
│  ├─ createRoom()
│  ├─ deleteRoom()
│  └─ selectRoom()
│
├─ WebSocket Management
│  ├─ connectWebSocket()
│  ├─ handleWebSocketMessage()
│  ├─ joinRoom()
│  └─ leaveRoom()
│
├─ Message Management
│  ├─ loadMessageHistory()
│  ├─ renderMessages()
│  ├─ addMessage()
│  └─ sendMessage()
│
└─ User Management
   ├─ updateUsersList()
   ├─ updateTypingIndicator()
   └─ handleTyping()
```

## Data Flow Patterns

### 1. Initial Page Load
```
Browser → GET / → Backend → Returns index.html
Browser → Loads CSS & JS
JavaScript → GET /api/chat/rooms → Backend → Returns room list
JavaScript → Renders rooms in sidebar
```

### 2. Create Room Flow
```
User clicks "New Room"
→ Show modal
→ User enters name/description
→ POST /api/chat/rooms
→ Backend validates & saves
→ Returns new room
→ Reload rooms list
→ Update UI
```

### 3. Join Room Flow
```
User clicks room
→ Show username modal
→ User enters username
→ Load message history (GET /api/chat/rooms/{id}/messages)
→ Render messages
→ Open WebSocket connection
→ Send authentication
→ Receive confirmation + users list
→ Enable chat input
→ Show chat screen
```

### 4. Send Message Flow
```
User types message
→ handleTyping() → Send typing indicator
→ User presses Enter/Send
→ sendMessage()
→ Send via WebSocket
→ Backend receives
→ Save to database
→ Broadcast to all users in room
→ All clients render new message
```

### 5. Leave Room Flow
```
User clicks "Leave Room"
→ Close WebSocket
→ Backend detects disconnect
→ Remove user from room
→ Broadcast "user left" to others
→ Update users list for remaining users
→ Client shows welcome screen
```

## State Management

### Server-Side State
```python
ConnectionManager:
  active_connections = {
    "1": {WebSocket1, WebSocket2, WebSocket3},  # Room 1 connections
    "2": {WebSocket4, WebSocket5}                # Room 2 connections
  }
  
  room_users = {
    "1": {"Alice", "Bob", "Carol"},
    "2": {"Dave", "Eve"}
  }
  
  connection_usernames = {
    WebSocket1: "Alice",
    WebSocket2: "Bob",
    ...
  }
  
  typing_users = {
    "1": {"Alice"},      # Alice is typing in room 1
    "2": set()           # No one typing in room 2
  }
```

### Client-Side State
```javascript
state = {
  ws: WebSocket,              // Current WebSocket connection
  currentRoom: {id, name},    // Current room object
  username: "Alice",          // Current user's name
  rooms: [...],               // All available rooms
  messages: [...],            // Current room's messages
  users: ["Alice", "Bob"],    // Online users in current room
  typingTimeout: null,        // Timeout for typing indicator
  reconnectAttempts: 0        // Number of reconnection attempts
}
```

## Security Considerations

### Current Implementation
- ✅ HTML escaping to prevent XSS
- ✅ Input validation with Pydantic
- ✅ Username length limits
- ✅ WebSocket message validation
- ✅ Room existence verification

### Production Recommendations
- 🔒 Add user authentication (JWT)
- 🔒 Add rate limiting
- 🔒 Use HTTPS/WSS
- 🔒 Add CSRF protection
- 🔒 Sanitize user input
- 🔒 Add content filtering
- 🔒 Implement permissions system
- 🔒 Add logging and monitoring

## Scalability Considerations

### Current Design (Single Server)
- Good for: 100-1000 concurrent users
- Limitations: In-memory state, single process

### Scaling Strategy
```
1. Horizontal Scaling
   ├─ Multiple FastAPI instances
   ├─ Load balancer (nginx)
   ├─ Redis for shared state
   └─ Redis Pub/Sub for message broadcasting

2. Database Scaling
   ├─ PostgreSQL instead of SQLite
   ├─ Connection pooling
   ├─ Read replicas
   └─ Caching layer (Redis)

3. WebSocket Scaling
   ├─ Sticky sessions (load balancer)
   ├─ Redis for cross-server communication
   └─ Message queue (RabbitMQ/Kafka)
```

## Error Handling

### Client-Side
- Connection failures → Show error, attempt reconnect
- WebSocket disconnect → Auto-reconnect (max 5 attempts)
- API errors → Display user-friendly messages
- Invalid input → Validation messages

### Server-Side
- Room not found → 404 error
- Duplicate room name → 400 error
- Database errors → Transaction rollback
- WebSocket errors → Cleanup and notify users

## Performance Optimizations

### Implemented
- Message limit on history fetch (100 messages)
- Efficient WebSocket broadcasting
- Minimal DOM manipulation
- CSS animations (GPU accelerated)
- Database indexes on foreign keys

### Future Improvements
- Message pagination/lazy loading
- Virtual scrolling for large chat history
- Image/file compression
- CDN for static assets
- Database query optimization
- Connection pooling
- Caching frequently accessed data

---

This architecture provides a solid foundation for a real-time chat system with room for future enhancements and scalability improvements.

