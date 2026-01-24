# Task Queue & Background Processing System

A full-stack task queue and background processing system built with FastAPI backend and vanilla HTML/JavaScript frontend. The system supports multiple task types with real-time progress monitoring, task cancellation, and retry capabilities.

## Features

### Backend (FastAPI + AsyncIO)
- **Asyncio-based Task Queue**: Efficient background task processing without external dependencies
- **Multiple Task Types**:
  - Data Processing: CSV analysis simulation (10-30 seconds)
  - Email Simulation: Mock email sending with delays
  - Image Processing: Simulated image resize/convert operations
- **Task Management**: Submit, monitor, cancel, and retry tasks
- **Real-time Progress**: Track task progress with percentage updates
- **Persistent Storage**: All task data stored in JSON file
- **RESTful API**: Clean REST endpoints for all operations

### Frontend (HTML + JavaScript)
- **Modern UI**: Beautiful gradient design with animations
- **Real-time Monitoring**: Auto-refresh for running tasks every 2 seconds
- **Task Submission**: Easy-to-use forms for different task types
- **Filtering**: Filter tasks by status and type
- **Detailed Views**: Modal dialogs showing complete task information
- **Progress Bars**: Visual progress indicators for running tasks
- **Responsive Design**: Works on desktop and mobile devices

### Task Statuses
- `PENDING`: Task queued, waiting to start
- `RUNNING`: Task currently executing
- `SUCCESS`: Task completed successfully
- `FAILED`: Task failed with error
- `CANCELLED`: Task was cancelled by user

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── tasks_data.json      # Persistent task storage (auto-generated)
├── frontend/
│   ├── index.html          # Main HTML page
│   ├── style.css           # Styling
│   └── app.js              # JavaScript logic
└── tests/
    ├── test_tasks.py       # Comprehensive test suite
    └── requirements.txt    # Test dependencies
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

3. Start the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Open `frontend/index.html` in a web browser, or serve it using a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080` in your browser.

## API Endpoints

### POST /api/tasks/submit
Submit a new background task.

**Request Body:**
```json
{
  "task_type": "data_processing",
  "parameters": {
    "rows": 1000
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "task_type": "data_processing",
  "status": "PENDING",
  "created_at": "2024-01-01T12:00:00Z",
  "progress": 0,
  "parameters": {"rows": 1000}
}
```

### GET /api/tasks/
List all tasks with optional filters.

**Query Parameters:**
- `status`: Filter by status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
- `task_type`: Filter by type (data_processing, email_simulation, image_processing)

**Response:**
```json
[
  {
    "id": "uuid",
    "task_type": "data_processing",
    "status": "SUCCESS",
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:00:01Z",
    "completed_at": "2024-01-01T12:00:30Z",
    "progress": 100,
    "result_data": {...}
  }
]
```

### GET /api/tasks/{task_id}
Get specific task details.

**Response:**
```json
{
  "id": "uuid",
  "task_type": "data_processing",
  "status": "SUCCESS",
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:00:01Z",
  "completed_at": "2024-01-01T12:00:30Z",
  "progress": 100,
  "result_data": {
    "total_rows": 1000,
    "processed": 1000,
    "statistics": {...}
  },
  "error_message": null
}
```

### DELETE /api/tasks/{task_id}
Cancel a pending or running task.

**Response:**
```json
{
  "id": "uuid",
  "status": "CANCELLED",
  "completed_at": "2024-01-01T12:00:15Z"
}
```

### POST /api/tasks/{task_id}/retry
Retry a failed task.

**Response:**
```json
{
  "id": "uuid",
  "status": "PENDING",
  "progress": 0,
  "error_message": null
}
```

## Task Types

### Data Processing
Simulates CSV data analysis with statistical computations.

**Parameters:**
- `rows` (int): Number of rows to process (default: 1000)

**Result Data:**
```json
{
  "total_rows": 1000,
  "processed": 1000,
  "statistics": {
    "mean": 95.3,
    "median": 98.1,
    "std_dev": 15.2,
    "min": 12.5,
    "max": 187.9
  }
}
```

### Email Simulation
Simulates sending emails to multiple recipients.

**Parameters:**
- `recipient_count` (int): Number of emails to send (default: 10)

**Result Data:**
```json
{
  "total_emails": 10,
  "sent": 9,
  "failed": 1,
  "recipients": [
    {"email": "user1@example.com", "status": "sent"},
    {"email": "user2@example.com", "status": "failed"}
  ]
}
```

### Image Processing
Simulates image resize/convert operations.

**Parameters:**
- `image_count` (int): Number of images to process (default: 5)
- `operation` (string): Operation type - "resize", "convert", or "compress"

**Result Data:**
```json
{
  "total_images": 5,
  "processed": 5,
  "operation": "resize",
  "images": [
    {
      "filename": "image_1.jpg",
      "original_size": "1920x1080",
      "processed_size": "800x600",
      "file_size_mb": 2.3
    }
  ]
}
```

## Running Tests

The test suite includes 20+ comprehensive tests covering:
- Task submission for all task types
- Task listing with filters
- Task retrieval
- Task cancellation
- Task retry logic
- Task execution and completion
- Progress updates
- Persistent storage
- Error handling
- Concurrent task submission

### Run Tests

1. Install test dependencies:
```bash
cd tests
pip install -r requirements.txt
```

2. Run the test suite:
```bash
pytest test_tasks.py -v
```

3. Run with coverage:
```bash
pytest test_tasks.py -v --cov=backend --cov-report=html
```

## Architecture

### Backend Architecture
- **FastAPI**: Modern async web framework
- **AsyncIO Queue**: In-memory task queue for background processing
- **Background Worker**: Dedicated async worker that processes tasks sequentially
- **JSON Storage**: Persistent task data storage
- **Task Executor**: Separate execution logic for each task type

### Frontend Architecture
- **Vanilla JavaScript**: No frameworks, pure JS for simplicity
- **Auto-refresh**: Polls backend every 2 seconds when tasks are running
- **Modal System**: Detailed task view in modal dialogs
- **Notification System**: Toast notifications for user feedback
- **Responsive Grid**: CSS Grid layout for modern responsive design

## Development

### Adding New Task Types

1. Add task type to `TaskType` enum in `main.py`:
```python
class TaskType(str, Enum):
    YOUR_TASK = "your_task"
```

2. Implement task execution function:
```python
async def your_task_executor(task_id: str, parameters: Dict[str, Any]):
    task = tasks_db[task_id]
    # Your task logic here
    # Update task.progress periodically
    # Return result data
    return {"result": "data"}
```

3. Add to task executor in `execute_task()`:
```python
elif task.task_type == TaskType.YOUR_TASK:
    result = await your_task_executor(task_id, task.parameters)
```

4. Update frontend with new task type option in `index.html` and `app.js`

## Security Considerations

- CORS is enabled for all origins (configure for production)
- No authentication implemented (add for production use)
- Task data stored in plain JSON (consider encryption for sensitive data)
- No rate limiting (implement for production)

## Performance

- Single worker processes tasks sequentially
- For high-throughput scenarios, consider:
  - Multiple worker processes
  - Celery with Redis/RabbitMQ
  - Distributed task queue systems

## License

MIT License - Feel free to use and modify as needed.

## Future Enhancements

- [ ] Task priority levels
- [ ] Task scheduling (run at specific time)
- [ ] Task dependencies (run after another task)
- [ ] WebSocket support for real-time updates
- [ ] Task result caching
- [ ] Task history and analytics
- [ ] User authentication and authorization
- [ ] Task templates and presets
- [ ] Export task results
- [ ] Email notifications on task completion
