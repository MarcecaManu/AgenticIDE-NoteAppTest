# Getting Started - Your First Task

Welcome! This guide will walk you through submitting your first background task.

## Prerequisites Check

Before starting, ensure you have:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Redis installed and running
- [ ] All dependencies installed (`pip install -r backend/requirements.txt`)

## Step-by-Step First Run

### Step 1: Start Redis

**Windows:**
```cmd
# Navigate to Redis directory and run:
redis-server.exe
```

**macOS:**
```bash
redis-server
# Or if installed via Homebrew:
brew services start redis
```

**Linux:**
```bash
sudo systemctl start redis
# Or:
redis-server
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### Step 2: Start Celery Worker

Open a new terminal:

**Windows:**
```cmd
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

**macOS/Linux:**
```bash
cd backend
celery -A celery_app worker --loglevel=info
```

You should see output like:
```
-------------- celery@hostname v5.3.6
--- ***** -----
-- ******* ---- Windows-10.0.26100
- *** --- * ---
- ** ---------- [tasks]
  . tasks.process_csv_data
  . tasks.send_emails
  . tasks.process_images
```

### Step 3: Start FastAPI Server

Open another new terminal:

**All Platforms:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Open Your Browser

Navigate to:
```
http://localhost:8000
```

You should see the Task Queue System interface! 🎉

## Submit Your First Task

### Option A: Using the Web Interface

1. **Select Task Type**: Choose "CSV Data Processing"
2. **Configure Parameters**:
   - Number of Rows: 1000
   - Processing Time: 15 seconds
3. **Click "Submit Task"**
4. **Watch the Magic**: You'll see:
   - Task appears in the list with "PENDING" status
   - After a moment, status changes to "RUNNING"
   - Progress bar fills up as task executes
   - Finally, status becomes "SUCCESS"
5. **View Results**: Click on the completed task to see results

### Option B: Using cURL

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "csv_processing",
    "input_params": {
      "num_rows": 1000,
      "processing_time": 15
    }
  }'
```

### Option C: Using Python

```python
import requests
import time

# Submit task
response = requests.post(
    "http://localhost:8000/api/tasks/submit",
    json={
        "task_type": "csv_processing",
        "input_params": {
            "num_rows": 1000,
            "processing_time": 15
        }
    }
)

task = response.json()
task_id = task["id"]
print(f"Task submitted: {task_id}")

# Monitor progress
while True:
    response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
    task = response.json()
    print(f"Status: {task['status']}, Progress: {task['progress']}%")
    
    if task["status"] in ["SUCCESS", "FAILED", "CANCELLED"]:
        break
    
    time.sleep(2)

print("Task completed!")
print(f"Results: {task['result_data']}")
```

## Understanding What Just Happened

### The Flow

```
You (Frontend)
    ↓ Submit task
FastAPI Server (backend/main.py)
    ↓ Create task record in database
    ↓ Send task to Redis queue
Celery Worker (backend/tasks.py)
    ↓ Pick up task from queue
    ↓ Update status to RUNNING
    ↓ Execute task logic
    ↓ Update progress periodically
    ↓ Store results
    ↓ Update status to SUCCESS
Frontend (auto-refresh every 3s)
    ↓ Display updated status
You see the completed task! 🎉
```

### Where is Everything?

- **Tasks in Database**: `backend/tasks.db` (SQLite)
- **Task Queue**: Redis (in-memory)
- **Task Execution**: Celery worker process
- **API Server**: FastAPI process
- **Frontend**: Served by FastAPI at `/`

## Try Different Task Types

### Email Sending Task

```json
{
  "task_type": "email_sending",
  "input_params": {
    "num_emails": 5,
    "subject": "Welcome Email",
    "delay_per_email": 1.0
  }
}
```

**What it does**: Simulates sending 5 emails with 1 second delay between each.

### Image Processing Task

```json
{
  "task_type": "image_processing",
  "input_params": {
    "num_images": 3,
    "target_width": 800,
    "target_height": 600
  }
}
```

**What it does**: Creates 3 dummy images and resizes them (2 seconds per image).

## Experiment with Features

### 1. Cancel a Running Task

1. Submit a long-running task (e.g., 30 seconds)
2. While it's running, click the "Cancel" button
3. Watch the status change to "CANCELLED"

### 2. Retry a Failed Task

1. Stop the Celery worker (Ctrl+C)
2. Submit a task
3. Task will stay in PENDING (worker is down)
4. Restart the Celery worker
5. The task will fail or you can cancel it
6. Click "Retry" to resubmit

### 3. Filter Tasks

1. Submit several tasks of different types
2. Use the filter dropdowns:
   - Filter by Status: "SUCCESS", "RUNNING", etc.
   - Filter by Type: "CSV Processing", "Email Sending", etc.

### 4. Monitor Progress

1. Submit a CSV processing task with 30 seconds duration
2. Watch the progress bar fill up in real-time
3. Click on the task to see detailed information

## Common Issues and Solutions

### Issue: "Cannot connect to Redis"

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# If not running, start it
redis-server
```

### Issue: "Tasks stay in PENDING"

**Cause**: Celery worker is not running or not connected

**Solution:**
```bash
# Check Celery worker terminal for errors
# Restart Celery worker
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

### Issue: "ModuleNotFoundError"

**Cause**: Missing dependencies

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Use a different port
uvicorn main:app --reload --host 0.0.0.0 --port 8001

# Update frontend/app.js:
# const API_BASE = 'http://localhost:8001/api';
```

### Issue: "Frontend not loading"

**Cause**: FastAPI server not running or wrong URL

**Solution:**
1. Check FastAPI terminal for errors
2. Verify server is running: `curl http://localhost:8000/api/health`
3. Check browser console for errors (F12)

## Understanding Task Statuses

| Status | Meaning | What to Do |
|--------|---------|------------|
| **PENDING** | Task is queued, waiting for worker | Wait (worker should pick it up soon) |
| **RUNNING** | Task is being executed right now | Watch progress bar |
| **SUCCESS** | Task completed successfully | View results by clicking task |
| **FAILED** | Task encountered an error | Check error message, then retry |
| **CANCELLED** | Task was cancelled by you | Retry if needed |

## Next Steps

Now that you've run your first task, explore more:

### 1. Read the Documentation
- [ ] **README.md** - Complete system overview
- [ ] **API_EXAMPLES.md** - More API usage examples
- [ ] **ARCHITECTURE.md** - How the system works internally

### 2. Run the Tests
```bash
cd tests
pytest -v
```

### 3. Explore the Code
- [ ] **backend/main.py** - API endpoints
- [ ] **backend/tasks.py** - Task implementations
- [ ] **frontend/app.js** - Frontend logic

### 4. Customize
- [ ] Add your own task type
- [ ] Modify task parameters
- [ ] Customize the UI
- [ ] Add new features

### 5. Deploy
- [ ] Try Docker Compose setup
- [ ] Deploy to cloud platform
- [ ] Set up monitoring

## Tips for Success

1. **Always have 3 terminals open**:
   - Terminal 1: Redis
   - Terminal 2: Celery worker
   - Terminal 3: FastAPI server

2. **Watch the logs**: They tell you what's happening

3. **Use the browser console** (F12): See frontend errors and API calls

4. **Start simple**: Try short tasks first (5-10 seconds)

5. **Experiment**: Try cancelling, retrying, filtering

6. **Read error messages**: They usually tell you what's wrong

## Quick Reference

### Start Everything (3 Terminals)

**Terminal 1:**
```bash
redis-server
```

**Terminal 2:**
```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

**Terminal 3:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Browser:**
```
http://localhost:8000
```

### Stop Everything

- Terminal 1, 2, 3: Press `Ctrl+C`
- Redis (if service): `brew services stop redis` (macOS) or `sudo systemctl stop redis` (Linux)

## Congratulations! 🎉

You've successfully set up and run your first background task!

The task queue system is now ready for:
- Processing real CSV files
- Sending actual emails (with SMTP)
- Processing real images
- Any other background tasks you can imagine

**Happy coding!** 🚀

---

## Need Help?

- Check **README.md** for detailed documentation
- Review **SETUP_GUIDE.md** for installation issues
- See **API_EXAMPLES.md** for more examples
- Read **ARCHITECTURE.md** to understand the system

