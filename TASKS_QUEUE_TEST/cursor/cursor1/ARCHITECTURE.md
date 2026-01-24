# System Architecture

## Overview

This is a full-stack task queue and background processing system built with modern web technologies.

## Components

### 1. Backend (FastAPI)

**File: `backend/main.py`**
- REST API server
- Handles HTTP requests
- Manages task lifecycle
- Serves frontend static files

**Endpoints:**
- `POST /api/tasks/submit` - Submit new tasks
- `GET /api/tasks/` - List all tasks with filters
- `GET /api/tasks/{task_id}` - Get specific task
- `DELETE /api/tasks/{task_id}` - Cancel task
- `POST /api/tasks/{task_id}/retry` - Retry failed task
- `GET /api/health` - Health check

### 2. Database Layer (SQLAlchemy)

**File: `backend/database.py`**
- SQLite database for persistence
- ORM models for tasks
- Session management

**Task Model:**
```python
- id: String (UUID)
- task_type: String
- status: String (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
- created_at: DateTime
- started_at: DateTime
- completed_at: DateTime
- result_data: JSON Text
- error_message: Text
- progress: Float (0-100)
- input_params: JSON Text
```

### 3. Task Queue (Celery + Redis)

**Files: `backend/celery_app.py`, `backend/tasks.py`**

**Celery Configuration:**
- Broker: Redis (message queue)
- Backend: Redis (result storage)
- Serializer: JSON
- Task tracking enabled

**Task Types:**
1. **CSV Processing** (`process_csv_data`)
   - Simulates processing large datasets
   - Updates progress in chunks
   - Returns statistics

2. **Email Sending** (`send_emails`)
   - Simulates sending multiple emails
   - Configurable delays
   - Tracks delivery status

3. **Image Processing** (`process_images`)
   - Creates and resizes images
   - Uses PIL/Pillow
   - Reports image details

### 4. Frontend (HTML/CSS/JavaScript)

**Files: `frontend/index.html`, `frontend/styles.css`, `frontend/app.js`**

**Features:**
- Task submission form with dynamic parameters
- Real-time task list with auto-refresh
- Task filtering by status and type
- Task detail modal
- Cancel and retry buttons
- Progress bars for running tasks

**UI Components:**
- Header with title
- Task submission form
- Filter controls
- Task list (auto-updating)
- Task detail modal

### 5. Testing (Pytest)

**Files: `tests/conftest.py`, `tests/test_api.py`, `tests/test_tasks.py`**

**Test Categories:**
1. API endpoint tests
2. Task execution tests
3. Error handling tests
4. Status transition tests
5. Progress tracking tests

## Data Flow

### Task Submission Flow

```
User (Frontend)
    ↓ POST /api/tasks/submit
FastAPI Server
    ↓ Create TaskModel (status: PENDING)
Database (SQLite)
    ↓ Submit to Celery
Redis Queue
    ↓ Worker picks up task
Celery Worker
    ↓ Update status to RUNNING
    ↓ Execute task logic
    ↓ Update progress periodically
    ↓ Store results
    ↓ Update status to SUCCESS/FAILED
Database (SQLite)
    ↓ Frontend polls for updates
User sees result
```

### Task Cancellation Flow

```
User clicks Cancel
    ↓ DELETE /api/tasks/{task_id}
FastAPI Server
    ↓ Validate task status
    ↓ Send revoke signal
Celery Control
    ↓ Terminate worker task
    ↓ Update status to CANCELLED
Database (SQLite)
    ↓ Frontend refreshes
User sees cancelled status
```

### Task Retry Flow

```
User clicks Retry
    ↓ POST /api/tasks/{task_id}/retry
FastAPI Server
    ↓ Load original task
    ↓ Create new task (new UUID)
    ↓ Copy input parameters
    ↓ Submit to queue
Celery Queue
    ↓ Execute as new task
User sees new task
```

## Key Design Decisions

### 1. Why Celery?
- Industry standard for Python task queues
- Robust distributed processing
- Built-in retry mechanisms
- Good monitoring tools

### 2. Why Redis?
- Fast in-memory broker
- Reliable message delivery
- Good for real-time systems
- Easy to set up

### 3. Why SQLite?
- Zero configuration
- Perfect for development
- Easy to migrate to PostgreSQL
- Good for single-server deployments

### 4. Why Plain JavaScript?
- No build step required
- Easy to understand
- Fast to develop
- No framework lock-in

### 5. Task Progress Updates
- Tasks update database directly
- No complex pub/sub needed
- Frontend polls every 3 seconds
- Simple and reliable

## Scalability Considerations

### Current System (Development)
- Single server
- SQLite database
- Local Redis
- One Celery worker

### Production Scaling Options

**Horizontal Scaling:**
1. Multiple Celery workers
2. Separate Redis instance
3. PostgreSQL database
4. Load balancer for API

**Vertical Scaling:**
1. More CPU for workers
2. More memory for Redis
3. Faster storage for database

**Advanced Features:**
1. Task priorities
2. Task routing (different queues)
3. Rate limiting
4. WebSocket for real-time updates
5. Task result caching
6. Dead letter queue
7. Task chaining/workflows

## Security Considerations

### Current Implementation
- CORS enabled for development
- No authentication
- No rate limiting
- No input validation beyond basics

### Production Requirements
1. Add authentication (JWT, OAuth)
2. Implement authorization (RBAC)
3. Add rate limiting
4. Input validation and sanitization
5. SQL injection prevention (using ORM)
6. XSS prevention
7. HTTPS only
8. Secure Redis with password
9. Environment variable secrets
10. API key for Celery monitoring

## Monitoring & Observability

### Current Logging
- Celery worker logs
- FastAPI access logs
- Console errors in frontend

### Production Monitoring
1. **Application Metrics:**
   - Task success/failure rates
   - Task execution times
   - Queue depth
   - Worker utilization

2. **Infrastructure Metrics:**
   - CPU, memory, disk usage
   - Redis memory usage
   - Database connections

3. **Tools:**
   - Flower (Celery monitoring)
   - Prometheus + Grafana
   - Sentry (error tracking)
   - ELK Stack (log aggregation)

## Error Handling Strategy

### Task Level
- Try-catch in task execution
- Update task status to FAILED
- Store error message
- Support retry mechanism

### API Level
- FastAPI exception handlers
- HTTP status codes
- Error details in response
- Validation errors

### Frontend Level
- API error handling
- User-friendly messages
- Graceful degradation
- Retry on network errors

## Performance Optimizations

### Current System
- Database indexes on task_id, status, task_type
- JSON serialization for efficiency
- Chunked progress updates
- Pagination for task list

### Potential Improvements
1. Redis caching for frequent queries
2. Database connection pooling
3. Batch database updates
4. WebSocket for real-time updates
5. Task result compression
6. CDN for frontend assets
7. Database query optimization
8. Celery task result expiration

## Testing Strategy

### Unit Tests
- Individual task functions
- API endpoint logic
- Database operations

### Integration Tests
- Full request/response cycle
- Task submission to completion
- Status transitions
- Error handling

### End-to-End Tests
- User workflows
- Task lifecycle
- Cancel and retry

### Test Coverage Goals
- >80% code coverage
- All API endpoints
- All task types
- Error scenarios
- Edge cases

## Future Enhancements

1. **WebSocket Support**
   - Real-time updates without polling
   - Lower server load
   - Better user experience

2. **Task Scheduling**
   - Cron-like scheduling
   - Periodic tasks
   - Delayed execution

3. **Task Chaining**
   - Complex workflows
   - Dependencies between tasks
   - Conditional execution

4. **Better UI**
   - React/Vue frontend
   - Better visualizations
   - Task timeline
   - Performance graphs

5. **Advanced Features**
   - Task priorities
   - Resource limits
   - Task templates
   - Bulk operations
   - Export results

6. **Multi-tenancy**
   - User accounts
   - Task isolation
   - Quota management
   - Usage statistics

This architecture provides a solid foundation for a production-grade task queue system while remaining simple enough for learning and development.

