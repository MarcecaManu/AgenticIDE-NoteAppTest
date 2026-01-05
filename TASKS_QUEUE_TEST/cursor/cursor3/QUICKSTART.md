# Quick Start Guide

Get the Task Queue system up and running in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation & Setup

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Server

**Option A: Using the run script**
```bash
python run.py
```

**Option B: Using uvicorn directly**
```bash
uvicorn backend.main:app --reload
```

**Option C: Using the backend main file**
```bash
cd backend
python main.py
```

### Step 3: Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Quick Test

### Using the Web Interface

1. Open http://localhost:8000
2. Select "Data Processing" task type
3. Set "Processing Time" to 10 seconds
4. Click "Submit Task"
5. Watch the real-time progress updates!

### Using the API

Submit a task via curl:

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "DATA_PROCESSING",
    "parameters": {
      "rows": 1000,
      "processing_time": 15
    }
  }'
```

List all tasks:

```bash
curl "http://localhost:8000/api/tasks/"
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=backend --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## Common Tasks

### Submit Different Task Types

**Email Simulation:**
```json
{
  "task_type": "EMAIL_SIMULATION",
  "parameters": {
    "recipient_count": 5,
    "delay_per_email": 2
  }
}
```

**Image Processing:**
```json
{
  "task_type": "IMAGE_PROCESSING",
  "parameters": {
    "image_count": 10,
    "operation": "resize",
    "target_size": "800x600"
  }
}
```

### Monitor Task Progress

The frontend automatically refreshes every 3 seconds. You can also manually refresh using the "Refresh Tasks" button.

### Cancel a Running Task

1. Find the task in the task list
2. Click "Cancel" button (only available for PENDING/RUNNING tasks)

### Retry a Failed Task

1. Find a failed task in the task list
2. Click "Retry" button
3. A new task will be created with the same parameters

## Troubleshooting

**Problem:** Port 8000 is already in use
```bash
# Use a different port
uvicorn backend.main:app --port 8001
```

**Problem:** Module not found errors
```bash
# Make sure you're in the project root directory
# Reinstall dependencies
pip install -r requirements.txt
```

**Problem:** Database errors
```bash
# Delete the database file and restart
rm backend/tasks.db
python run.py
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API documentation at http://localhost:8000/docs
- Check out the test suite in the `tests/` directory
- Customize task types in `backend/task_workers.py`

## Project Structure

```
├── backend/           # FastAPI backend
│   ├── main.py       # API endpoints
│   ├── database.py   # Database models
│   ├── task_queue.py # Task queue manager
│   └── task_workers.py # Task implementations
├── frontend/         # HTML/CSS/JS frontend
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── tests/           # Test suite
│   ├── test_api.py
│   └── test_task_workers.py
├── requirements.txt # Python dependencies
├── run.py          # Quick start script
└── README.md       # Full documentation
```

## Features Overview

✅ **Task Submission** - Submit background tasks via web UI or API
✅ **Real-time Monitoring** - Watch task progress live
✅ **Multiple Task Types** - Data processing, email, image processing
✅ **Task Management** - Cancel, retry, filter tasks
✅ **Persistent Storage** - All tasks saved to database
✅ **Comprehensive Tests** - 17+ automated tests
✅ **Modern UI** - Beautiful, responsive interface
✅ **REST API** - Full-featured RESTful API

Enjoy! 🎉


