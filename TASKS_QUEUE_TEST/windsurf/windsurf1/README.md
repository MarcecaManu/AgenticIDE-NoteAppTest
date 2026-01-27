# Task Queue & Background Processing System

A full-stack task queue and background processing system built with FastAPI backend and HTML/JavaScript frontend.

## Features

### Backend (FastAPI + Asyncio)
- **REST API** at `/api/tasks/` with 5 endpoints
- **Three Task Types**:
  - Data Processing: CSV-style data analysis (10-15 seconds)
  - Email Simulation: Mock email sending with delays (4-6 seconds)
  - Image Processing: Mock image resize/convert (6-9 seconds)
- **Task Statuses**: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
- **Progress Reporting**: Real-time progress updates for long-running tasks
- **Persistent Storage**: JSON-based task data storage
- **Asyncio Task Queue**: Non-blocking background task execution

### Frontend (HTML + JavaScript)
- **Modern UI**: Beautiful gradient design with animations
- **Real-time Updates**: Auto-refresh every 2 seconds
- **Task Management**: Submit, monitor, cancel, and retry tasks
- **Statistics Dashboard**: Live task counts by status
- **Filtering**: Filter tasks by status and type
- **Progress Bars**: Visual progress indicators for running tasks
- **Notifications**: User-friendly success/error messages

### API Endpoints

#### POST /api/tasks/submit
Submit a new background task
```json
{
  "task_type": "data_processing",
  "parameters": {"rows": 1000}
}
```

#### GET /api/tasks/
List all tasks (with optional filters)
- Query params: `status`, `task_type`

#### GET /api/tasks/{task_id}
Get specific task status and results

#### DELETE /api/tasks/{task_id}
Cancel a pending task

#### POST /api/tasks/{task_id}/retry
Retry a failed task

## Project Structure

```
.
├── backend/
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── tasks.json        # Persistent task storage (auto-generated)
├── frontend/
│   └── index.html        # Frontend application
├── tests/
│   ├── test_tasks.py     # Comprehensive test suite
│   └── requirements.txt  # Test dependencies
└── README.md
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

1. Open `frontend/index.html` in a web browser, or
2. Serve it with a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080`

## Running Tests

1. Navigate to the tests directory:
```bash
cd tests
```

2. Install test dependencies:
```bash
pip install -r requirements.txt
```

3. Run the test suite:
```bash
pytest test_tasks.py -v
```

## Test Coverage

The test suite includes 20+ comprehensive tests covering:

1. **Task Submission**: All three task types (data processing, email, image)
2. **Task Listing**: List all tasks, filter by status, filter by type
3. **Task Retrieval**: Get specific task, handle non-existent tasks
4. **Task Cancellation**: Cancel pending tasks, prevent cancelling running tasks
5. **Task Retry**: Retry failed tasks, prevent retrying non-failed tasks
6. **Task Execution**: Verify successful completion of all task types
7. **Progress Tracking**: Monitor progress updates during execution
8. **Persistent Storage**: Verify data is saved to JSON file
9. **Error Handling**: Invalid task types, malformed requests
10. **Timestamps**: Verify created_at, started_at, completed_at fields

## Usage Examples

### Data Processing Task
```json
{
  "task_type": "data_processing",
  "parameters": {
    "rows": 1000
  }
}
```
Processes data rows and returns statistics (sum, average, min, max).

### Email Simulation Task
```json
{
  "task_type": "email_simulation",
  "parameters": {
    "recipients": ["user1@example.com", "user2@example.com"],
    "subject": "Hello World"
  }
}
```
Simulates sending emails to multiple recipients.

### Image Processing Task
```json
{
  "task_type": "image_processing",
  "parameters": {
    "images": ["image1.jpg", "image2.jpg", "image3.jpg"],
    "operation": "resize"
  }
}
```
Simulates image processing operations.

## Task Data Model

Each task contains:
- `id`: Unique task identifier (UUID)
- `task_type`: Type of task (data_processing, email_simulation, image_processing)
- `status`: Current status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
- `created_at`: ISO timestamp when task was created
- `started_at`: ISO timestamp when task started execution
- `completed_at`: ISO timestamp when task completed
- `result_data`: Task results (varies by task type)
- `error_message`: Error message if task failed
- `progress`: Progress percentage (0-100)
- `parameters`: Task-specific parameters

## Architecture

### Backend Architecture
- **FastAPI**: Modern Python web framework with automatic API documentation
- **Asyncio**: Non-blocking task execution using Python's async/await
- **TaskQueue Class**: Manages task lifecycle and execution
- **JSON Storage**: Simple, persistent task data storage
- **CORS Enabled**: Allows frontend to communicate with backend

### Frontend Architecture
- **Vanilla JavaScript**: No frameworks, pure JavaScript for simplicity
- **Fetch API**: Modern HTTP client for API communication
- **Auto-refresh**: Polls backend every 2 seconds for updates
- **Responsive Design**: Works on desktop and mobile devices

## Security Features
- CORS configuration for cross-origin requests
- Input validation with Pydantic models
- Error handling for all endpoints
- Safe task cancellation

## Performance
- Non-blocking task execution
- Efficient asyncio event loop
- Minimal memory footprint
- Scalable task queue design

## Future Enhancements
- Add Redis/Celery for distributed task processing
- Implement WebSocket for real-time updates
- Add user authentication and authorization
- Support for task priorities and scheduling
- Task result caching
- Database backend (PostgreSQL/MongoDB)

## License
MIT License

## Author
Built with FastAPI, Asyncio, and modern web technologies.
