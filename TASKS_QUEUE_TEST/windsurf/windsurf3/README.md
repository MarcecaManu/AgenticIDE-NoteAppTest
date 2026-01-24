# Task Queue & Background Processing System

A full-stack task queue and background processing system built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

### Backend (FastAPI + AsyncIO)
- **REST API** at `/api/tasks/` with complete task management
- **Async Task Queue** using Python's asyncio for background processing
- **Three Task Types**:
  - Data Processing (CSV analysis simulation)
  - Email Simulation (bulk email sending with delays)
  - Image Processing (resize/convert operations)
- **Task Statuses**: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
- **Progress Reporting** for long-running tasks
- **Persistent Storage** using JSON file storage
- **Comprehensive Error Handling**

### Frontend (HTML + JavaScript)
- **Modern UI** with gradient design and animations
- **Real-time Task Monitoring** (auto-refresh every 2 seconds)
- **Task Submission** with dynamic parameter forms
- **Filter & Search** by status and task type
- **Live Statistics Dashboard**
- **Task Actions**: Cancel pending tasks, retry failed tasks
- **Progress Bars** for running tasks
- **Detailed Result Display** with JSON formatting

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/submit` | Submit a new background task |
| GET | `/api/tasks/` | List all tasks (with optional filters) |
| GET | `/api/tasks/{task_id}` | Get specific task status and results |
| DELETE | `/api/tasks/{task_id}` | Cancel a pending/running task |
| POST | `/api/tasks/{task_id}/retry` | Retry a failed task |

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # Pydantic models and enums
│   ├── storage.py           # Persistent task storage
│   ├── task_queue.py        # AsyncIO task queue manager
│   ├── task_workers.py      # Task worker implementations
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main UI
│   └── app.js               # Frontend logic and API calls
├── tests/
│   └── test_api.py          # Comprehensive test suite (15 tests)
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip

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

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Open `index.html` in a web browser, or serve it using a simple HTTP server:
```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

## Running Tests

From the project root directory:

```bash
cd tests
pytest test_api.py -v
```

The test suite includes 15 comprehensive tests covering:
- Task submission for all task types
- Task listing and filtering
- Task status retrieval
- Task cancellation
- Task retry logic
- Error handling
- Task execution and status updates

## Usage Examples

### Submit a Data Processing Task

```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "data_processing",
    "parameters": {
      "rows": 1000,
      "processing_time": 15
    }
  }'
```

### Submit an Email Simulation Task

```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "email_simulation",
    "parameters": {
      "recipient_count": 10,
      "delay_per_email": 1,
      "subject": "Test Email"
    }
  }'
```

### Submit an Image Processing Task

```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "image_processing",
    "parameters": {
      "image_count": 5,
      "operation": "resize",
      "processing_time": 10
    }
  }'
```

### List All Tasks

```bash
curl http://localhost:8000/api/tasks/
```

### Filter Tasks by Status

```bash
curl http://localhost:8000/api/tasks/?status=RUNNING
```

### Get Specific Task

```bash
curl http://localhost:8000/api/tasks/{task_id}
```

### Cancel a Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id}
```

### Retry a Failed Task

```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/retry
```

## Task Types & Parameters

### Data Processing
- `rows` (int): Number of rows to process (100-10000)
- `processing_time` (int): Processing duration in seconds (5-30)

### Email Simulation
- `recipient_count` (int): Number of recipients (1-50)
- `delay_per_email` (float): Delay between emails in seconds (0.5-5)
- `subject` (string): Email subject line

### Image Processing
- `image_count` (int): Number of images to process (1-20)
- `operation` (string): Operation type (resize/convert/compress)
- `processing_time` (int): Processing duration in seconds (5-30)

## Architecture

### Task Queue System
- Uses Python's `asyncio.Queue` for task management
- Background worker processes tasks asynchronously
- Non-blocking task execution with progress reporting
- Automatic status updates throughout task lifecycle

### Storage System
- JSON-based persistent storage
- Async file operations for thread safety
- Automatic data serialization/deserialization
- Task history preservation

### Task Workers
- Modular worker implementations for each task type
- Progress callback system for real-time updates
- Simulated long-running operations
- Comprehensive error handling

## Security Features
- CORS enabled for cross-origin requests
- Input validation using Pydantic models
- Error message sanitization
- Safe task cancellation

## Performance
- Async/await for non-blocking operations
- Efficient task queue management
- Real-time progress updates
- Optimized JSON storage with locking

## Future Enhancements
- Redis/Celery integration for distributed processing
- WebSocket support for real-time updates
- Task scheduling and cron-like functionality
- Task priority queues
- Database backend (PostgreSQL/MongoDB)
- User authentication and authorization
- Task result caching
- Metrics and monitoring dashboard

## License
MIT License

## Author
Built with FastAPI, AsyncIO, and modern web technologies.
