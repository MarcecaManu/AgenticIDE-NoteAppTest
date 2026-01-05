# Task Queue & Background Processing System

A full-stack application for managing and monitoring background tasks with real-time status updates.

## Features

- ✅ **Multiple Task Types**: CSV processing, email sending, and image processing
- ✅ **Real-time Monitoring**: Track task progress with live updates
- ✅ **Task Management**: Submit, cancel, and retry tasks
- ✅ **Persistent Storage**: All task data stored in SQLite database
- ✅ **RESTful API**: Complete REST API for task operations
- ✅ **Modern UI**: Clean, responsive interface built with HTML/CSS/JavaScript
- ✅ **Comprehensive Tests**: 20+ automated tests covering all functionality

## Architecture

### Backend
- **FastAPI**: High-performance async web framework
- **Celery**: Distributed task queue for background processing
- **Redis**: Message broker and result backend
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Persistent data storage

### Frontend
- **Plain HTML/CSS/JavaScript**: No framework dependencies
- **Real-time Updates**: Auto-refresh every 3 seconds
- **Responsive Design**: Works on all screen sizes

### Task Types

1. **CSV Data Processing** (10-30 seconds)
   - Simulates processing large CSV files
   - Calculates statistics (sum, avg, min, max)
   - Reports progress in real-time

2. **Email Sending** (variable duration)
   - Simulates sending multiple emails
   - Configurable delay between emails
   - Tracks sent/failed emails

3. **Image Processing** (2 seconds per image)
   - Simulates resizing/converting images
   - Creates dummy images and resizes them
   - Reports processed image details

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and session
│   ├── schemas.py           # Pydantic schemas
│   ├── tasks.py             # Celery task definitions
│   ├── celery_app.py        # Celery configuration
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Styles
│   └── app.js               # JavaScript application
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_api.py          # API endpoint tests
│   └── test_tasks.py        # Task execution tests
└── README.md
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Redis server (for Celery)

### Setup Instructions

1. **Clone the repository** (or create the project structure)

2. **Install Redis**:
   - **Windows**: Download from https://github.com/microsoftarchive/redis/releases
   - **macOS**: `brew install redis`
   - **Linux**: `sudo apt-get install redis-server`

3. **Start Redis**:
   ```bash
   # Windows (from Redis directory)
   redis-server

   # macOS/Linux
   redis-server
   ```

4. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

5. **Start the Celery worker** (in a separate terminal):
   ```bash
   cd backend
   celery -A celery_app worker --loglevel=info --pool=solo
   ```
   Note: On Windows, use `--pool=solo` flag

6. **Start the FastAPI server** (in another terminal):
   ```bash
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Open your browser** and navigate to:
   ```
   http://localhost:8000
   ```

## API Endpoints

### Submit Task
```http
POST /api/tasks/submit
Content-Type: application/json

{
  "task_type": "csv_processing",
  "input_params": {
    "num_rows": 1000,
    "processing_time": 15
  }
}
```

### List Tasks
```http
GET /api/tasks/
GET /api/tasks/?status=RUNNING
GET /api/tasks/?task_type=csv_processing
```

### Get Task Details
```http
GET /api/tasks/{task_id}
```

### Cancel Task
```http
DELETE /api/tasks/{task_id}
```

### Retry Task
```http
POST /api/tasks/{task_id}/retry
```

### Health Check
```http
GET /api/health
```

## Task Statuses

- **PENDING**: Task is queued but not started
- **RUNNING**: Task is currently executing
- **SUCCESS**: Task completed successfully
- **FAILED**: Task encountered an error
- **CANCELLED**: Task was cancelled by user

## Running Tests

Run all tests:
```bash
cd tests
pytest -v
```

Run specific test file:
```bash
pytest test_api.py -v
```

Run with coverage:
```bash
pytest --cov=../backend --cov-report=html
```

## Test Coverage

The test suite includes 20+ tests covering:

1. ✅ Task submission for all task types
2. ✅ Invalid task type handling
3. ✅ Task listing and filtering
4. ✅ Status-based filtering
5. ✅ Type-based filtering
6. ✅ Specific task retrieval
7. ✅ Non-existent task handling
8. ✅ Task cancellation
9. ✅ Cancel validation
10. ✅ Task retry for failed tasks
11. ✅ Task retry for cancelled tasks
12. ✅ Retry validation
13. ✅ Status transitions
14. ✅ Progress tracking
15. ✅ CSV processing execution
16. ✅ Email sending execution
17. ✅ Image processing execution
18. ✅ Error handling
19. ✅ Health check endpoint
20. ✅ Database operations

## Usage Guide

### Submitting a Task

1. Select a task type from the dropdown
2. Configure task parameters
3. Click "Submit Task"
4. Task will appear in the task list with PENDING status

### Monitoring Tasks

- Tasks auto-refresh every 3 seconds
- Progress bar shows completion percentage for running tasks
- Click on any task to view detailed information

### Managing Tasks

- **Cancel**: Click the "Cancel" button on pending/running tasks
- **Retry**: Click the "Retry" button on failed/cancelled tasks
- **Filter**: Use the filter dropdowns to show specific tasks

### Task Parameters

**CSV Processing:**
- Number of Rows: 100-10,000
- Processing Time: 5-60 seconds

**Email Sending:**
- Number of Emails: 1-100
- Email Subject: Custom text
- Delay per Email: 0.5-5 seconds

**Image Processing:**
- Number of Images: 1-20
- Target Width: 100-2000 pixels
- Target Height: 100-2000 pixels

## Configuration

### Environment Variables

```bash
# Redis URL (default: redis://localhost:6379/0)
export REDIS_URL=redis://localhost:6379/0
```

### Database

The application uses SQLite by default. The database file `tasks.db` will be created automatically in the backend directory.

## Troubleshooting

### Redis Connection Error
- Ensure Redis server is running
- Check Redis is accessible at `localhost:6379`
- Verify no firewall blocking the connection

### Celery Worker Not Starting
- On Windows, use `--pool=solo` flag
- Ensure all dependencies are installed
- Check Redis connection

### Tasks Not Executing
- Verify Celery worker is running and connected
- Check Redis server is running
- Look for errors in Celery worker logs

### Frontend Not Loading
- Ensure FastAPI server is running
- Check browser console for errors
- Verify API_BASE URL in `frontend/app.js` matches your server

## Development

### Adding New Task Types

1. Create task function in `backend/tasks.py`:
```python
@celery_app.task(bind=True)
def my_new_task(self, task_id: str, input_params: dict):
    # Implementation
    pass
```

2. Add to TASK_FUNCTIONS in `backend/main.py`:
```python
TASK_FUNCTIONS = {
    "my_new_task": my_new_task,
    # ... existing tasks
}
```

3. Update frontend form in `frontend/index.html`

4. Add tests in `tests/test_api.py`

## Performance Considerations

- **Concurrent Tasks**: Celery can process multiple tasks simultaneously
- **Redis Performance**: Redis is in-memory, very fast for task queuing
- **Database**: SQLite is suitable for development; use PostgreSQL for production
- **Progress Updates**: Tasks update database every chunk to show progress

## Production Deployment

For production environments:

1. Use PostgreSQL instead of SQLite
2. Use a dedicated Redis instance
3. Add authentication and authorization
4. Implement rate limiting
5. Use environment variables for configuration
6. Add proper logging and monitoring
7. Use gunicorn or similar for FastAPI
8. Deploy Celery workers as separate services
9. Add error tracking (e.g., Sentry)
10. Implement task result expiration

## License

MIT License - Feel free to use this project for learning or as a base for your applications.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Author

Built as a demonstration of task queue and background processing patterns.

