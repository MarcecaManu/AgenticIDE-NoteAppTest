# Task Queue & Background Processing System

A full-stack task queue and background processing system built with FastAPI and vanilla JavaScript.

## Features

- **Background Task Processing**: Execute long-running tasks asynchronously
- **Multiple Task Types**: 
  - Data Processing (CSV analysis simulation)
  - Email Simulation
  - Image Processing
- **Real-time Monitoring**: Track task progress and status updates
- **Task Management**: Submit, cancel, and retry tasks
- **Persistent Storage**: SQLite database for task data
- **RESTful API**: Clean API design with FastAPI
- **Modern UI**: Responsive web interface with real-time updates

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Database models
│   ├── database.py          # Database configuration
│   ├── task_queue.py        # Asyncio task queue manager
│   └── task_workers.py      # Task worker implementations
├── frontend/
│   ├── index.html           # Main HTML page
│   ├── styles.css           # Styling
│   └── app.js               # JavaScript application logic
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests
│   └── test_task_workers.py # Task worker tests
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Installation

1. **Clone the repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the backend server**
   ```bash
   python -m uvicorn backend.main:app --reload
   ```

   The server will start at `http://localhost:8000`

2. **Access the web interface**
   
   Open your browser and navigate to `http://localhost:8000`

## API Endpoints

### Submit Task
```http
POST /api/tasks/submit
Content-Type: application/json

{
  "task_type": "data_processing",
  "parameters": {
    "rows": 1000
  }
}
```

### List Tasks
```http
GET /api/tasks/
GET /api/tasks/?status=PENDING
GET /api/tasks/?task_type=data_processing
```

### Get Task Details
```http
GET /api/tasks/{task_id}
```

### Cancel Task
```http
DELETE /api/tasks/{task_id}
```

### Retry Failed Task
```http
POST /api/tasks/{task_id}/retry
```

## Task Types

### Data Processing
Simulates CSV file analysis (10-30 seconds)
```json
{
  "task_type": "data_processing",
  "parameters": {
    "rows": 1000
  }
}
```

### Email Simulation
Simulates sending emails with delays
```json
{
  "task_type": "email_simulation",
  "parameters": {
    "count": 5
  }
}
```

### Image Processing
Simulates image resize/convert operations
```json
{
  "task_type": "image_processing",
  "parameters": {
    "count": 3,
    "operation": "resize"
  }
}
```

## Task Statuses

- **PENDING**: Task is queued and waiting to be processed
- **RUNNING**: Task is currently being executed
- **SUCCESS**: Task completed successfully
- **FAILED**: Task failed with an error
- **CANCELLED**: Task was cancelled by user

## Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ -v --cov=backend --cov-report=html
```

## Architecture

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Asyncio**: Built-in Python async/await for task queue management
- **SQLite**: Lightweight database for persistent storage

### Frontend
- **Vanilla JavaScript**: No frameworks, pure JS
- **Modern CSS**: Responsive design with gradients and animations
- **Real-time Updates**: Auto-refresh every 2 seconds

### Task Queue
The system uses asyncio-based task queuing:
1. Tasks are submitted via REST API
2. Added to an asyncio Queue
3. Worker processes tasks from the queue
4. Progress updates are written to database
5. Frontend polls for status updates

## Development

### Adding New Task Types

1. Create a new worker class in `backend/task_workers.py`:
```python
class MyCustomWorker(TaskWorker):
    @staticmethod
    async def execute(task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Your task logic here
        return {"result": "data"}
```

2. Register the worker in `TASK_WORKERS` dictionary:
```python
TASK_WORKERS = {
    "my_custom_task": MyCustomWorker,
    # ... other workers
}
```

3. Update the frontend task type selector in `frontend/index.html`

### Database Schema

The `Task` model includes:
- `id`: Unique task identifier (UUID)
- `task_type`: Type of task
- `status`: Current status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
- `created_at`: Task creation timestamp
- `started_at`: Task start timestamp
- `completed_at`: Task completion timestamp
- `result_data`: JSON result data
- `error_message`: Error details if failed
- `progress`: Progress percentage (0-100)
- `parameters`: JSON task parameters

## Production Considerations

For production deployment, consider:

1. **Use PostgreSQL or MySQL** instead of SQLite
2. **Add authentication** and authorization
3. **Implement rate limiting** on API endpoints
4. **Use Redis or RabbitMQ** for distributed task queue
5. **Add logging** and monitoring (e.g., ELK stack)
6. **Deploy with Docker** and orchestration (Kubernetes)
7. **Add WebSocket support** for real-time updates instead of polling
8. **Implement task retries** with exponential backoff
9. **Add task priority levels**
10. **Implement worker scaling** based on queue size

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

