# Task Queue & Background Processing System

A full-stack application for managing and monitoring background tasks with real-time progress tracking.

## 🚀 Features

- **FastAPI Backend**: RESTful API with comprehensive task management endpoints
- **Celery + Redis**: Robust asynchronous task processing
- **Multiple Task Types**:
  - Data Processing (CSV analysis with 10-30 second processing time)
  - Email Simulation (batch email sending with delays)
  - Image Processing (resize/convert/compress operations)
- **Task Management**:
  - Submit tasks with custom parameters
  - Monitor task progress in real-time
  - Cancel pending/running tasks
  - Retry failed tasks
  - Filter and search by status/type
- **Persistent Storage**: SQLite database for task data
- **Modern Frontend**: Responsive HTML/CSS/JavaScript interface with auto-refresh
- **Comprehensive Testing**: 19 automated tests covering all functionality

## 📁 Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application with REST API
│   ├── celery_app.py        # Celery configuration
│   ├── tasks.py             # Task implementations
│   ├── models.py            # Pydantic models
│   ├── database.py          # Database models and setup
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── index.html           # Main HTML interface
│   ├── styles.css           # Styling
│   └── app.js               # JavaScript logic
└── tests/
    ├── __init__.py
    ├── conftest.py          # Pytest fixtures
    └── test_api.py          # API tests (19 tests)
```

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.9+
- Redis server (for Celery broker/backend)

### 1. Install Redis

**Windows** (using Chocolatey):
```powershell
choco install redis-64
redis-server
```

**Linux/macOS**:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
redis-server

# macOS
brew install redis
redis-server
```

### 2. Install Python Dependencies

```powershell
cd backend
pip install -r requirements.txt
```

### 3. Start the Backend Services

**Terminal 1 - Start FastAPI server:**
```powershell
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Celery worker:**
```powershell
cd backend
celery -A celery_app.celery_app worker --loglevel=info --pool=solo
```

> **Note**: On Windows, use `--pool=solo` for Celery. On Linux/macOS, you can omit this flag.

### 4. Open the Frontend

Open `frontend/index.html` in your web browser, or serve it with a simple HTTP server:

```powershell
cd frontend
python -m http.server 8080
```

Then navigate to `http://localhost:8080` in your browser.

## 🧪 Running Tests

```powershell
cd tests
pytest test_api.py -v
```

Expected output: All 19 tests should pass.

## 📡 API Endpoints

### Submit Task
```
POST /api/tasks/submit
Body: {
  "task_type": "data_processing|email_simulation|image_processing",
  "input_data": { ... }
}
```

**Note**: The API accepts both lowercase (`data_processing`) and uppercase (`DATA_PROCESSING`) task types, and supports both `input_data` and `parameters` field names for maximum compatibility.

### List Tasks
```
GET /api/tasks/
Query params: ?status=PENDING&task_type=data_processing&limit=100&offset=0
```

### Get Task Details
```
GET /api/tasks/{task_id}
```

### Cancel Task
```
DELETE /api/tasks/{task_id}
```

### Retry Failed Task
```
POST /api/tasks/{task_id}/retry
```

### Health Check
```
GET /health
```

## 📊 Task Types & Parameters

The API supports flexible parameter naming for compatibility:

### Data Processing
Analyzes CSV data with configurable row count.

**Format 1** (lowercase):
```json
{
  "task_type": "data_processing",
  "input_data": {
    "rows": 1000
  }
}
```

**Format 2** (uppercase, alternative field names):
```json
{
  "task_type": "DATA_PROCESSING",
  "parameters": {
    "num_rows": 1000,
    "processing_time": 15
  }
}
```

### Email Simulation
Simulates sending emails with delays.

**Format 1**:
```json
{
  "task_type": "email_simulation",
  "input_data": {
    "recipient_count": 10,
    "delay_per_email": 1
  }
}
```

**Format 2**:
```json
{
  "task_type": "EMAIL_SIMULATION",
  "parameters": {
    "num_emails": 10,
    "delay_per_email": 1,
    "subject": "Test Email"
  }
}
```

### Image Processing
Simulates image resize/convert/compress operations.

**Format 1**:
```json
{
  "task_type": "image_processing",
  "input_data": {
    "image_count": 5,
    "operation": "resize",
    "target_size": "800x600"
  }
}
```

**Format 2**:
```json
{
  "task_type": "IMAGE_PROCESSING",
  "parameters": {
    "num_images": 5,
    "target_size": "800x600",
    "output_format": "PNG"
  }
}
```

## 🔄 Task Statuses

- **PENDING**: Task submitted, waiting to be processed
- **RUNNING**: Task currently being executed
- **SUCCESS**: Task completed successfully
- **FAILED**: Task encountered an error
- **CANCELLED**: Task was cancelled by user

## 🎯 Features Demonstration

1. **Real-time Progress**: Submit a data processing task and watch the progress bar update
2. **Concurrent Tasks**: Submit multiple tasks and see them execute in parallel
3. **Task Cancellation**: Cancel a running task and see it stop
4. **Retry Logic**: Manually fail a task (by simulating errors) and retry it
5. **Filtering**: Use the status and type filters to organize tasks
6. **Auto-refresh**: Enable auto-refresh to automatically update task statuses every 5 seconds

## 🐛 Troubleshooting

### Redis Connection Error
- Ensure Redis is running: `redis-cli ping` should return `PONG`
- Check Redis URL in `backend/celery_app.py` (default: `redis://localhost:6379/0`)

### Celery Worker Not Starting
- On Windows, make sure to use `--pool=solo` flag
- Check that Redis is accessible
- Verify Python path includes the backend directory

### Frontend Not Connecting to Backend
- Ensure FastAPI is running on `http://localhost:8000`
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/app.js`

### Tests Failing
- Ensure no other tasks.db or test_tasks.db files exist
- Stop any running Celery workers during testing
- Run tests from the tests directory

## 📝 License

MIT License - feel free to use this project for learning and development.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify as needed!

## 📧 Contact

For questions or issues, please open an issue in the repository.

---

**Built with**: FastAPI, Celery, Redis, SQLAlchemy, HTML5, CSS3, Vanilla JavaScript
