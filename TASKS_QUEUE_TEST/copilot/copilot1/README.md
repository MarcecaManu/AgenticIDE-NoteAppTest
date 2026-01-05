# Task Queue & Background Processing System

A full-stack application for managing background tasks with real-time progress monitoring. Built with FastAPI backend and vanilla HTML/JavaScript frontend.

## Features

- ✅ **Multiple Task Types**:
  - Data Processing (CSV analysis)
  - Email Simulation
  - Image Processing (resize/convert)

- ✅ **Real-time Monitoring**:
  - Live progress updates
  - Task status tracking
  - Result viewing

- ✅ **Task Management**:
  - Submit new tasks
  - Cancel pending/running tasks
  - Retry failed tasks
  - Filter and search tasks

- ✅ **REST API**:
  - Complete RESTful endpoints
  - JSON responses
  - CORS enabled

- ✅ **Persistent Storage**:
  - JSON-based task storage
  - Automatic task recovery on restart

- ✅ **Comprehensive Tests**:
  - 20+ automated tests
  - Full coverage of endpoints and features

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── models.py         # Data models and schemas
│   ├── storage.py        # Persistent storage
│   ├── task_queue.py     # Task queue implementation
│   ├── task_handlers.py  # Task type handlers
│   └── requirements.txt  # Python dependencies
├── frontend/
│   ├── index.html        # Web interface
│   └── app.js           # Frontend JavaScript
├── tests/
│   ├── __init__.py
│   └── test_task_queue.py  # Automated tests
├── data/
│   └── tasks.json        # Task storage (created automatically)
├── pytest.ini            # Test configuration
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or navigate to the project directory**:
   ```powershell
   cd c:\Users\marce\Desktop\Tesi\AgenticIDE-NoteAppTest\TASKS_QUEUE_TEST\copilot\copilot1
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r backend/requirements.txt
   ```

## Running the Application

### Start the Backend Server

```powershell
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

### Access the Frontend

Open your browser and navigate to:
```
http://localhost:8000/
```

Or use the API documentation at:
```
http://localhost:8000/docs
```

## API Endpoints

### Submit a Task
```http
POST /api/tasks/submit
Content-Type: application/json

{
  "task_type": "DATA_PROCESSING",
  "parameters": {
    "num_rows": 1000,
    "processing_time": 15
  }
}
```

### List All Tasks
```http
GET /api/tasks/
GET /api/tasks/?status=PENDING
GET /api/tasks/?task_type=DATA_PROCESSING
```

### Get Task Details
```http
GET /api/tasks/{task_id}
```

### Cancel a Task
```http
DELETE /api/tasks/{task_id}
```

### Retry a Failed Task
```http
POST /api/tasks/{task_id}/retry
```

### Health Check
```http
GET /api/health
```

## Task Types

### 1. Data Processing
Simulates CSV data analysis with configurable parameters.

**Parameters**:
- `num_rows` (int): Number of rows to process (default: 1000)
- `processing_time` (int): Time in seconds (default: 10-30 random)

**Result**:
```json
{
  "rows_processed": 1000,
  "total_sum": 500000,
  "average": 500.0,
  "max_value": 999,
  "min_value": 1,
  "processing_time": 15
}
```

### 2. Email Simulation
Simulates sending emails with delays and occasional failures.

**Parameters**:
- `num_emails` (int): Number of emails to send (default: 10)
- `delay_per_email` (float): Delay per email in seconds (default: 1.0)
- `subject` (str): Email subject (default: "Test Email")

**Result**:
```json
{
  "total_emails": 10,
  "sent_successfully": 9,
  "failed": 1,
  "sent_emails": [...],
  "failed_emails": [...]
}
```

### 3. Image Processing
Simulates image resize/conversion operations.

**Parameters**:
- `num_images` (int): Number of images to process (default: 5)
- `target_size` (str): Target dimensions (default: "800x600")
- `output_format` (str): Output format (default: "PNG")

**Result**:
```json
{
  "total_images": 5,
  "processed_successfully": 5,
  "output_format": "PNG",
  "target_size": "800x600",
  "processed_images": [...],
  "total_size_saved": 1500000
}
```

## Task Statuses

- **PENDING**: Task is queued but not yet started
- **RUNNING**: Task is currently executing
- **SUCCESS**: Task completed successfully
- **FAILED**: Task encountered an error
- **CANCELLED**: Task was cancelled by user

## Running Tests

Execute the test suite:

```powershell
pytest tests/ -v
```

Run specific test class:

```powershell
pytest tests/test_task_queue.py::TestTaskSubmission -v
```

Run with coverage:

```powershell
pytest tests/ --cov=backend --cov-report=html
```

## Test Coverage

The test suite includes 20+ tests covering:

1. **Task Submission Tests** (4 tests):
   - Data processing task submission
   - Email simulation task submission
   - Image processing task submission
   - Minimal parameter submission

2. **Task Retrieval Tests** (5 tests):
   - Get all tasks
   - Get task by ID
   - Get nonexistent task
   - Filter by status
   - Filter by type

3. **Task Cancellation Tests** (4 tests):
   - Cancel pending task
   - Cancel running task
   - Cannot cancel completed task
   - Cancel nonexistent task

4. **Task Retry Tests** (4 tests):
   - Retry failed task
   - Retry via API
   - Cannot retry successful task
   - Retry nonexistent task

5. **Task Execution Tests** (4 tests):
   - Data processing execution
   - Email simulation execution
   - Image processing execution
   - Progress updates

6. **Error Handling Tests** (3 tests):
   - Invalid task type
   - Malformed request
   - Health check

7. **Storage Tests** (4 tests):
   - Add and retrieve task
   - Update task
   - Delete task
   - Filter by status

## Configuration

### Backend Configuration

The backend uses the following default settings:

- **Host**: localhost
- **Port**: 8000
- **Storage Path**: `data/tasks.json`
- **Auto-refresh Interval**: 2 seconds (frontend)

### Customizing Storage Path

You can customize the storage path in [backend/main.py](backend/main.py):

```python
storage = TaskStorage("custom/path/tasks.json")
```

### Customizing Task Parameters

Modify default parameters in [backend/task_handlers.py](backend/task_handlers.py).

## Development

### Project Architecture

1. **Backend Layer**:
   - `main.py`: FastAPI application and route handlers
   - `models.py`: Pydantic models and enums
   - `storage.py`: JSON-based persistent storage
   - `task_queue.py`: Asyncio-based task queue manager
   - `task_handlers.py`: Task execution logic

2. **Frontend Layer**:
   - `index.html`: UI structure and styling
   - `app.js`: Task management logic and API calls

3. **Test Layer**:
   - `test_task_queue.py`: Comprehensive test suite

### Adding a New Task Type

1. Add task type to `TaskType` enum in `models.py`
2. Create handler function in `task_handlers.py`
3. Register handler in `task_queue.py`
4. Add UI form in `index.html`
5. Update parameter extraction in `app.js`
6. Write tests in `test_task_queue.py`

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```powershell
uvicorn backend.main:app --reload --port 8001
```

Then update the API_BASE in `frontend/app.js` to `http://localhost:8001/api`.

### Tasks Not Persisting

Check that the `data/` directory exists and is writable:

```powershell
mkdir data -ErrorAction SilentlyContinue
```

### CORS Issues

If accessing from a different domain, update CORS settings in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://yourdomain.com"],
    ...
)
```

## Performance Considerations

- The task queue processes one task at a time (single worker)
- For production, consider using Celery with Redis for distributed processing
- Task storage uses JSON files - for large-scale deployments, use a database
- Frontend auto-refreshes every 2 seconds - adjust as needed

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Ensure all tests pass
6. Submit a pull request

## Support

For issues or questions, please open an issue in the project repository.

---

**Built with ❤️ using FastAPI and vanilla JavaScript**
