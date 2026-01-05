# Quick Start Guide

Get up and running with the Task Queue system in 3 simple steps!

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Start the Server

Option A - Using the run script (recommended):
```bash
python run.py
```

Option B - Using uvicorn directly:
```bash
python -m uvicorn backend.main:app --reload
```

## Step 3: Open Your Browser

Navigate to: `http://localhost:8000`

That's it! You should see the Task Queue Manager interface.

## Try It Out

1. **Submit a Task**: 
   - Select a task type (Data Processing, Email Simulation, or Image Processing)
   - Configure parameters
   - Click "Submit Task"

2. **Monitor Progress**: 
   - Watch the task progress in real-time
   - Tasks will show progress bars as they execute

3. **Manage Tasks**:
   - Click on any task to view detailed results
   - Cancel pending/running tasks
   - Retry failed tasks

## Running Tests

```bash
pytest
```

For detailed test output:
```bash
pytest -v
```

For test coverage:
```bash
pytest --cov=backend --cov-report=html
```

## API Testing with curl

### Submit a task:
```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"task_type": "data_processing", "parameters": {"rows": 1000}}'
```

### List all tasks:
```bash
curl http://localhost:8000/api/tasks/
```

### Get specific task:
```bash
curl http://localhost:8000/api/tasks/{task_id}
```

### Cancel a task:
```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id}
```

### Retry a failed task:
```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/retry
```

## Troubleshooting

### Port already in use
If port 8000 is already in use, you can specify a different port:
```bash
python -m uvicorn backend.main:app --reload --port 8080
```

### Database locked
If you get a database locked error, delete the `tasks.db` file and restart:
```bash
rm tasks.db
python run.py
```

### Import errors
Make sure you're running commands from the project root directory and have installed all dependencies.

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API endpoints
- Check out the test files to understand the system better
- Try modifying task parameters to see different behaviors

## Support

For issues or questions, please check:
1. The main README.md file
2. The code comments in backend/
3. The test files in tests/

Happy task processing! 🚀

