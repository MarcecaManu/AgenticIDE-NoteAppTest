# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│                    (HTML + CSS + JS)                        │
│                                                             │
│  ┌──────────────┐                    ┌─────────────────┐   │
│  │ Room         │                    │ Chat            │   │
│  │ Selection    │◄──────────────────►│ Interface       │   │
│  │ Screen       │                    │                 │   │
│  └──────────────┘                    │ • Messages      │   │
│                                      │ • Online Users  │   │
│                                      │ • Typing        │   │
│                                      └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                        │                      ▲
                        │ HTTP REST            │ WebSocket
                        ▼                      │
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│                      (FastAPI)                              │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    main.py                           │  │
│  │                                                      │  │
│  │  REST Endpoints:          WebSocket:                │  │
│  │  • POST /api/chat/rooms   • /ws/chat/{room_id}      │  │
│  │  • GET /api/chat/rooms    • Join/Leave              │  │
│  │  • GET .../messages       • Broadcasting            │  │
│  │  • DELETE .../rooms       • Typing Indicators       │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                      │             │
│          ┌─────────────┴──────────┬──────────┴──────┐      │
│          ▼                        ▼                 ▼      │
│  ┌─────────────┐         ┌────────────────┐  ┌──────────┐ │
│  │  database.py│         │ connection_    │  │schemas.py│ │
│  │             │         │ manager.py     │  │          │ │
│  │ • Room      │         │                │  │Validation│ │
│  │ • Message   │         │ • Connect      │  │Models    │ │
│  │ • SQLAlchemy│         │ • Disconnect   │  │          │ │
│  │             │         │ • Broadcast    │  │          │ │
│  └─────────────┘         │ • User Mgmt    │  └──────────┘ │
│          │               └────────────────┘               │
│          ▼                                                 │
│  ┌─────────────┐                                          │
│  │  chat.db    │                                          │
│  │  (SQLite)   │                                          │
│  └─────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Creating a Room (REST)
```
Frontend → POST /api/chat/rooms → Backend → Database → Response
```

### 2. Listing Rooms (REST)
```
Frontend → GET /api/chat/rooms → Backend → Database → JSON Response
```

### 3. Real-time Messaging (WebSocket)
```
User A types message
    ↓
WebSocket.send()
    ↓
Backend receives message
    ↓
Save to Database
    ↓
ConnectionManager.broadcast_to_room()
    ↓
All connected users receive message (including User A)
```

### 4. Typing Indicator (WebSocket)
```
User starts typing
    ↓
Send typing event (is_typing: true)
    ↓
Backend tracks typing users
    ↓
Broadcast typing list to all users
    ↓
Other users see "User is typing..."
```

## Component Responsibilities

### Backend Components

| Component | Responsibility |
|-----------|---------------|
| **main.py** | FastAPI app, routes, WebSocket endpoint |
| **database.py** | SQLAlchemy models, DB connection |
| **schemas.py** | Pydantic validation schemas |
| **connection_manager.py** | WebSocket state, broadcasting |

### Frontend Components

| Component | Responsibility |
|-----------|---------------|
| **index.html** | UI structure, screens |
| **styles.css** | Styling, animations, responsive design |
| **app.js** | API calls, WebSocket, UI updates |

## Message Types

### WebSocket Client → Server

```json
// Send message
{"type": "message", "content": "Hello!"}

// Typing indicator
{"type": "typing", "is_typing": true}
```

### WebSocket Server → Client

```json
// New message
{"type": "message", "id": 1, "username": "Alice", "content": "Hi!", "timestamp": "..."}

// User joined
{"type": "join", "username": "Bob", "content": "Bob joined the room", "timestamp": "..."}

// User left
{"type": "leave", "username": "Charlie", "content": "Charlie left", "timestamp": "..."}

// Online users
{"type": "user_list", "users": ["Alice", "Bob"], "timestamp": "..."}

// Typing users
{"type": "typing", "users": ["Alice"], "timestamp": "..."}
```

## Database Schema

```
┌──────────────┐           ┌──────────────────┐
│   rooms      │           │    messages      │
├──────────────┤           ├──────────────────┤
│ id (PK)      │───┐       │ id (PK)          │
│ name         │   │       │ room_id (FK)     │──┐
│ created_at   │   │       │ username         │  │
└──────────────┘   │       │ content          │  │
                   │       │ timestamp        │  │
                   └───────│                  │◄─┘
                    1:N    └──────────────────┘
```

## Connection States

```
                    ┌──────────┐
                    │  CLOSED  │
                    └────┬─────┘
                         │ connect()
                         ▼
                 ┌───────────────┐
        ┌────────│  CONNECTING   │
        │        └───────┬───────┘
        │                │ onopen
        │                ▼
        │        ┌───────────────┐
        │   ┌────│   CONNECTED   │────┐
        │   │    └───────────────┘    │
        │   │            │             │
        │   │ send()     │ receive()  │ onerror/onclose
        │   │            │             │
        │   └────────────┴─────────────┘
        │                │
        │                ▼
        │        ┌───────────────┐
        └───────►│ DISCONNECTED  │
   reconnect     └───────┬───────┘
   (max 5)              │
                        ▼
                ┌───────────────┐
                │  RECONNECT    │
                │   ATTEMPT     │
                └───────────────┘
```

## Test Coverage Map

```
REST API Tests
├── Room Management
│   ├── Create room ✓
│   ├── Duplicate room error ✓
│   ├── List rooms ✓
│   └── Delete room ✓
└── Messages
    ├── Get empty messages ✓
    └── Get from non-existent room ✓

WebSocket Tests
├── Connection
│   ├── Connect to room ✓
│   ├── Connect to non-existent room ✓
│   └── Leave notification ✓
├── Messaging
│   ├── Broadcast to multiple users ✓
│   └── Message persistence ✓
├── Features
│   └── Typing indicator ✓
└── Data Integrity
    └── Cascade delete ✓
```

## Performance Characteristics

- **Message Latency:** <100ms (local network)
- **Concurrent Users per Room:** Tested with 2+ users
- **Database:** SQLite (suitable for small-medium deployments)
- **WebSocket Protocol:** RFC 6455 compliant
- **Auto-reconnect:** Up to 5 attempts with exponential backoff (2s, 4s, 6s, 8s, 10s)

## Security Considerations

- ✅ Input validation (Pydantic schemas)
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (HTML escaping)
- ✅ CORS configuration
- ⚠️ No authentication (out of scope for this demo)
- ⚠️ No rate limiting (would add in production)
- ⚠️ No message encryption (would add in production)
