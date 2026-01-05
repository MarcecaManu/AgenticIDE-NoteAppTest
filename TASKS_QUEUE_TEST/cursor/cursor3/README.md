# Task Queue & Background Processing System

A full-stack application for managing and monitoring background tasks with real-time updates.

## Features

- **FastAPI Backend** with RESTful API
- **Asyncio-based Task Queue** (no external dependencies like Redis/Celery required)
- **Three Task Types**:
  - Data Processing (CSV analysis simulation)
  - Email Simulation (bulk email sending)
  - Image Processing (resize/convert operations)
- **Real-time Progress Monitoring**
- **Persistent Storage** with SQLite
- **Modern Frontend** with vanilla JavaScript
- **Comprehensive Test Suite** (17+ tests)

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database models and connection
│   ├── task_queue.py        # Asyncio task queue manager
│   └── task_workers.py      # Task worker implementations
├── frontend/
│   ├── index.html           # Main HTML interface
│   ├── styles.css           # Styling
│   └── app.js               # JavaScript logic
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration
│   ├── test_api.py          # API endpoint tests
│   └── test_task_workers.py # Worker logic tests
├── requirements.txt
└── README.md
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the backend server**:
   ```bash
   cd backend
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Access the application**:
   - Open your browser and navigate to: `http://localhost:8000`
   - API documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### Submit a Task
```http
POST /api/tasks/submit
Content-Type: application/json

{
  "task_type": "DATA_PROCESSING",
  "parameters": {
    "rows": 1000,
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

### Get Specific Task
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

## Task Types and Parameters

### 1. Data Processing
Simulates CSV file analysis with configurable duration.

**Parameters**:
- `rows` (int): Number of rows to process (default: 1000)
- `processing_time` (int): Processing duration in seconds (default: 15)

**Result**:
- Total rows processed
- Statistics (sum, average, min, max)
- Processing time

### 2. Email Simulation
Simulates bulk email sending with delays.

**Parameters**:
- `recipient_count` (int): Number of emails to send (default: 5)
- `delay_per_email` (int): Delay between emails in seconds (default: 2)

**Result**:
- Total emails sent
- Failed emails count
- List of recipients with statuses

### 3. Image Processing
Simulates image resize/convert operations.

**Parameters**:
- `image_count` (int): Number of images to process (default: 10)
- `operation` (string): "resize" or "convert"
- `target_size` (string): Target dimensions (default: "800x600")

**Result**:
- Processed images count
- Details for each image
- Size reduction statistics

## Task Statuses

- `PENDING`: Task is queued and waiting to start
- `RUNNING`: Task is currently being processed
- `SUCCESS`: Task completed successfully
- `FAILED`: Task failed with an error
- `CANCELLED`: Task was cancelled by user

## Frontend Features

- **Submit Tasks**: Choose task type and configure parameters
- **Real-time Monitoring**: Automatic updates every 3 seconds
- **Progress Bars**: Visual progress indication for running tasks
- **Filter & Search**: Filter by status or task type
- **Task Details**: View complete task information in modal
- **Actions**: Cancel pending tasks, retry failed tasks
- **Responsive Design**: Works on desktop and mobile

## Running Tests

Run the comprehensive test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=backend --cov-report=html
```

### Test Coverage

The test suite includes 17+ tests covering:
- ✅ Health check endpoint
- ✅ Task submission for all three task types
- ✅ Invalid task type handling
- ✅ Task listing and filtering
- ✅ Task retrieval
- ✅ Task cancellation
- ✅ Task retry logic
- ✅ Worker execution for all task types
- ✅ Worker cancellation
- ✅ Worker factory function
- ✅ Error handling

## Development

### Adding New Task Types

1. Create a new worker class in `task_workers.py`:
   ```python
   class MyNewWorker(TaskWorker):
       async def execute(self) -> Dict[str, Any]:
           # Implementation
           pass
   ```

2. Register it in the `TASK_WORKERS` dictionary

3. Add the task type to `TaskType` enum in `database.py`

4. Update the frontend form with new parameters

### Database

The application uses SQLite for persistent storage. The database file `tasks.db` is created automatically in the backend directory.

To reset the database, simply delete `tasks.db` and restart the server.

## Architecture

### Backend Architecture
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **Asyncio**: Native Python async/await for task queue
- **Pydantic**: Data validation and serialization

### Task Queue Design
- Tasks are stored in SQLite for persistence
- Asyncio event loop manages concurrent task execution
- Progress callbacks update database in real-time
- Workers can be cancelled gracefully

### Frontend Architecture
- Vanilla JavaScript (no frameworks)
- Real-time updates via polling
- Responsive CSS Grid layout
- Modal-based detail views

## Configuration

Key configuration options in `database.py`:
- `DATABASE_URL`: SQLite database location

Key configuration in `frontend/app.js`:
- `API_BASE`: API base URL
- Auto-refresh interval: 3000ms

## Troubleshooting

### Port Already in Use
If port 8000 is already in use:
```bash
uvicorn backend.main:app --port 8001
```

### Database Locked
If you encounter database locked errors, ensure only one server instance is running.

### Tasks Not Starting
Check the terminal for error messages. Ensure all dependencies are installed correctly.

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Redis/Celery integration option
- [ ] Task scheduling (cron-like)
- [ ] Task dependencies and workflows
- [ ] User authentication
- [ ] Task result export (CSV, JSON)
- [ ] Docker containerization
- [ ] Horizontal scaling support

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


