# System Architecture

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Browser                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Frontend (HTML + CSS + JavaScript)                  │   │
│  │  - Task submission forms                             │   │
│  │  - Real-time status monitoring                       │   │
│  │  - Task management UI                                │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST API
                       │ Auto-refresh (2s)
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Server                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  REST API Endpoints (main.py)                        │   │
│  │  - POST /api/tasks/submit                            │   │
│  │  - GET /api/tasks/                                   │   │
│  │  - GET /api/tasks/{task_id}                          │   │
│  │  - DELETE /api/tasks/{task_id}                       │   │
│  │  - POST /api/tasks/{task_id}/retry                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Task Queue Manager (task_queue.py)                   │  │
│  │  - Asyncio Queue                                      │  │
│  │  - Task submission                                    │  │
│  │  - Concurrent execution                               │  │
│  │  - Progress tracking                                  │  │
│  └────────────────────────┬──────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼──────────────────────────────┐  │
│  │  Task Workers (task_workers.py)                       │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  DataProcessingWorker                            │ │  │
│  │  │  - CSV analysis simulation                       │ │  │
│  │  │  - 10-30 second execution                        │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  EmailSimulationWorker                           │ │  │
│  │  │  - Email sending simulation                      │ │  │
│  │  │  - Delay simulation                              │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  ImageProcessingWorker                           │ │  │
│  │  │  - Image resize/convert simulation               │ │  │
│  │  │  - Progress updates                              │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  └────────────────────────┬──────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────┘
                            │
                            │ SQLAlchemy ORM
┌───────────────────────────▼─────────────────────────────────┐
│                    SQLite Database                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Tasks Table                                         │   │
│  │  - id (UUID, primary key)                            │   │
│  │  - task_type (indexed)                               │   │
│  │  - status (indexed)                                  │   │
│  │  - created_at, started_at, completed_at              │   │
│  │  - result_data (JSON)                                │   │
│  │  - error_message                                     │   │
│  │  - progress (0-100)                                  │   │
│  │  - parameters (JSON)                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Request Flow

### 1. Task Submission Flow
```
User clicks "Submit Task"
    ↓
Frontend collects parameters
    ↓
POST /api/tasks/submit
    ↓
API validates task type & parameters
    ↓
Task Queue creates Task in database (PENDING)
    ↓
Task added to asyncio Queue
    ↓
Return task_id to frontend
    ↓
Frontend starts polling for updates
```

### 2. Task Execution Flow
```
Worker retrieves task from Queue
    ↓
Update task status to RUNNING
    ↓
Worker executes task logic
    ↓
Worker updates progress periodically
    ↓
Task completes successfully or fails
    ↓
Update task status (SUCCESS/FAILED)
    ↓
Store result_data or error_message
```

### 3. Task Monitoring Flow
```
Frontend polls every 2 seconds
    ↓
GET /api/tasks/?status=...&task_type=...
    ↓
API queries database with filters
    ↓
Return filtered task list
    ↓
Frontend updates UI with new data
    ↓
Progress bars, status badges update
```

## Component Responsibilities

### Frontend (`frontend/`)
**Purpose**: User interface for task management

**Responsibilities**:
- Display task submission forms
- Collect and validate user input
- Show task list with filtering
- Real-time status updates via polling
- Task detail modal display
- Cancel and retry actions

**Technologies**:
- HTML5 for structure
- CSS3 for styling
- Vanilla JavaScript for logic
- Fetch API for HTTP requests

### API Layer (`backend/main.py`)
**Purpose**: REST API endpoints

**Responsibilities**:
- Route HTTP requests
- Validate request data (Pydantic)
- Call task queue methods
- Query database
- Return JSON responses
- Error handling

**Technologies**:
- FastAPI framework
- Pydantic models
- Dependency injection

### Task Queue (`backend/task_queue.py`)
**Purpose**: Manage task lifecycle

**Responsibilities**:
- Accept task submissions
- Maintain task queue
- Dispatch tasks to workers
- Handle task cancellation
- Implement retry logic
- Manage concurrent execution

**Technologies**:
- Python asyncio
- asyncio.Queue
- Async/await patterns

### Task Workers (`backend/task_workers.py`)
**Purpose**: Execute actual task logic

**Responsibilities**:
- Implement task-specific logic
- Update progress during execution
- Generate results
- Handle task-specific errors
- Simulate long-running operations

**Technologies**:
- Python async functions
- Asyncio sleep for delays
- Random for simulations

### Database Layer (`backend/database.py`, `backend/models.py`)
**Purpose**: Data persistence

**Responsibilities**:
- Define data schema
- Manage database connections
- Provide session management
- Handle transactions

**Technologies**:
- SQLAlchemy ORM
- SQLite database
- Context managers

## Data Flow Diagram

```
┌─────────┐         ┌─────────┐         ┌──────────┐
│  User   │────────►│Frontend │────────►│   API    │
└─────────┘  Input  └─────────┘  HTTP   └────┬─────┘
                                              │
                                              │ Create
                                              ▼
┌──────────┐        ┌──────────┐        ┌──────────┐
│ Database │◄───────│Task Queue│◄───────│   Task   │
└────┬─────┘ Store  └────┬─────┘ Submit └──────────┘
     │                   │
     │ Query             │ Dispatch
     ▼                   ▼
┌──────────┐        ┌──────────┐
│   API    │        │ Workers  │
└────┬─────┘        └────┬─────┘
     │                   │
     │ Response          │ Update
     ▼                   ▼
┌──────────┐        ┌──────────┐
│Frontend  │        │ Database │
└──────────┘        └──────────┘
```

## State Machine

```
Task Status State Machine:

    PENDING ───────► RUNNING ───────► SUCCESS
       │                │
       │                ├──────────► FAILED
       │                │
       └────────────────┴──────────► CANCELLED

Transitions:
- PENDING → RUNNING: Worker starts processing
- RUNNING → SUCCESS: Task completes successfully
- RUNNING → FAILED: Task encounters error
- PENDING → CANCELLED: User cancels before execution
- RUNNING → CANCELLED: User cancels during execution
- FAILED → PENDING: User retries (creates new task)
```

## Concurrency Model

```
┌─────────────────────────────────────────┐
│          Main Event Loop                │
│  ┌──────────────────────────────────┐   │
│  │    FastAPI Request Handlers      │   │
│  │    (Multiple concurrent requests)│   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Task Queue Worker             │   │
│  │    (Single worker, processes     │   │
│  │     tasks sequentially)          │   │
│  └──────────────────────────────────┘   │
│                                          │
│  ┌──────────────────────────────────┐   │
│  │    Task Execution                │   │
│  │    (Multiple tasks can run       │   │
│  │     concurrently as async tasks) │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Scalability Considerations

### Current Architecture (Development)
- Single process
- Asyncio for concurrency
- SQLite database
- In-memory queue

### Production Architecture (Recommended)
```
┌──────────────┐
│ Load Balancer│
└──────┬───────┘
       │
   ┌───┴────┬────────┬────────┐
   ▼        ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐
│FastAPI ││FastAPI ││FastAPI │
│Server 1││Server 2││Server 3│
└───┬────┘└───┬────┘└───┬────┘
    │         │         │
    └────┬────┴────┬────┘
         ▼         ▼
    ┌─────────┐┌─────────┐
    │  Redis  ││PostgreSQL│
    │ Queue   ││ Database │
    └────┬────┘└─────────┘
         │
    ┌────┴─────┬────────┬────────┐
    ▼          ▼        ▼        ▼
┌────────┐┌────────┐┌────────┐
│Worker 1││Worker 2││Worker 3│
└────────┘└────────┘└────────┘
```

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5 | Structure |
| Frontend | CSS3 | Styling |
| Frontend | JavaScript ES6+ | Logic |
| API | FastAPI | Web framework |
| API | Pydantic | Validation |
| Queue | Python asyncio | Async operations |
| Workers | Python async/await | Task execution |
| ORM | SQLAlchemy | Database abstraction |
| Database | SQLite | Data persistence |
| Testing | Pytest | Test framework |
| Server | Uvicorn | ASGI server |

## Security Layers

Current implementation (development):
```
Frontend → API → Database
  (No authentication)
```

Production recommendation:
```
Frontend → [HTTPS] → [API Gateway] → [JWT Auth] → API → [Encryption] → Database
                       ↓
                   [Rate Limiting]
                   [Input Validation]
                   [CORS Policy]
```

## Performance Characteristics

- **Task Submission**: < 50ms
- **Task Retrieval**: < 10ms (indexed queries)
- **Concurrent Tasks**: Limited by asyncio (hundreds of concurrent tasks)
- **Database**: SQLite suitable for < 100k tasks
- **Frontend Updates**: 2-second polling interval

## Extension Points

1. **New Task Types**: Add worker class in `task_workers.py`
2. **New Endpoints**: Add route in `main.py`
3. **Custom Storage**: Replace database module
4. **Queue Backend**: Replace asyncio queue with Redis
5. **Authentication**: Add middleware in FastAPI
6. **Notifications**: Add WebSocket support

This architecture provides a solid foundation that can grow from a development prototype to a production-scale system.

