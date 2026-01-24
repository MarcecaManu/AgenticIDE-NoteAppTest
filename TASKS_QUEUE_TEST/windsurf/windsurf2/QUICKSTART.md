# Quick Start Guide

## Installation & Setup

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Install Test Dependencies (Optional)
```bash
cd tests
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using Batch Scripts (Windows)

**Start Backend:**
```bash
start_backend.bat
```

**Start Frontend (in a new terminal):**
```bash
start_frontend.bat
```

### Option 2: Manual Start

**Start Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
```bash
cd frontend
python -m http.server 8080
```

Or simply open `frontend/index.html` directly in your browser.

## Access the Application

- **Frontend UI**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Running Tests

### Using Batch Script (Windows)
```bash
run_tests.bat
```

### Manual
```bash
cd tests
pytest test_tasks.py -v
```

## Quick Usage Guide

### 1. Submit a Task
- Select task type (Data Processing, Email Simulation, or Image Processing)
- Configure parameters
- Click "Submit Task"

### 2. Monitor Tasks
- Tasks appear automatically in the list
- Running tasks show progress bars
- Auto-refresh every 2 seconds for active tasks

### 3. View Task Details
- Click "View Details" on any task
- See complete information including results and errors

### 4. Cancel Tasks
- Click "Cancel" on pending or running tasks
- Task status changes to CANCELLED

### 5. Retry Failed Tasks
- Click "Retry" on failed tasks
- Task resets and re-enters the queue

## Task Types & Parameters

### Data Processing
- **Rows**: 100-10000 (default: 1000)
- **Duration**: 10-30 seconds
- **Output**: Statistical analysis results

### Email Simulation
- **Recipients**: 1-100 (default: 10)
- **Duration**: 5-20 seconds
- **Output**: Email sending results with success/failure counts

### Image Processing
- **Images**: 1-20 (default: 5)
- **Operation**: resize, convert, or compress
- **Duration**: 10-40 seconds
- **Output**: Processed image details

## Troubleshooting

### Backend won't start
- Ensure port 8000 is not in use
- Check Python and pip are installed
- Verify all dependencies are installed

### Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_BASE_URL in `frontend/app.js`

### Tests failing
- Ensure backend dependencies are installed
- Check test dependencies are installed
- Verify no backend server is running during tests

## API Testing with curl

### Submit a task
```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"task_type":"data_processing","parameters":{"rows":1000}}'
```

### List all tasks
```bash
curl http://localhost:8000/api/tasks/
```

### Get specific task
```bash
curl http://localhost:8000/api/tasks/{task_id}
```

### Cancel a task
```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id}
```

### Retry a failed task
```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/retry
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check out the test suite in `tests/test_tasks.py` for usage examples
- Customize task types and parameters for your use case
