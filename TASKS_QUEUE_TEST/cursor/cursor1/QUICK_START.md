# Quick Start Guide - Fixed System

## ✅ Issue Fixed

The **circular import issue** has been resolved. The system is now ready to use!

### What was the problem?
- `celery_app.py` was importing from `tasks.py`
- `tasks.py` was importing from `celery_app.py`
- This created a circular dependency causing import errors

### How was it fixed?
- Used Celery's `include=['tasks']` parameter instead of direct imports
- This tells Celery to auto-discover tasks without creating circular dependencies
- Cleared Redis queue of old invalid task messages

---

## 🚀 Starting the System

### Step 1: Verify Setup (Recommended)
```bash
cd backend
python verify_setup.py
```

You should see:
```
[OK] celery_app imported successfully
[OK] tasks imported successfully
[OK] database imported successfully
[OK] FastAPI app imported successfully
[OK] Redis is running and accessible
[OK] Database initialized
[OK] All expected tasks are registered
[SUCCESS] ALL CHECKS PASSED - System is ready!
```

### Step 2: Start Celery Worker (Terminal 1)
```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

**Expected output (confirms tasks are registered):**
```
[tasks]
  . tasks.process_csv_data
  . tasks.process_images
  . tasks.send_emails
```

### Step 3: Start FastAPI Server (Terminal 2)
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 4: Open Browser
```
http://localhost:8000
```

---

## ✅ Verification

### Test 1: Health Check
```bash
curl http://localhost:8000/api/health
```

Expected: `{"status":"healthy","timestamp":"..."}`

### Test 2: Submit a Task
```bash
curl -X POST "http://localhost:8000/api/tasks/submit" ^
  -H "Content-Type: application/json" ^
  -d "{\"task_type\": \"csv_processing\", \"input_params\": {\"num_rows\": 100, \"processing_time\": 5}}"
```

Expected: Task JSON with `"status": "PENDING"`

Watch the Celery worker terminal - you should see the task being processed!

### Test 3: Run Test Suite
```bash
pytest tests\ -v
```

Expected: **24 tests passed** ✅

---

## 📁 Key Files Modified

1. **backend/celery_app.py**
   - Fixed: Added `include=['tasks']` parameter to Celery() constructor
   - Removed: Direct import of tasks (which caused circular import)

2. **backend/clear_redis.py** (new)
   - Clears Redis queue of old invalid tasks

3. **backend/verify_setup.py** (new)
   - Verifies all imports work correctly
   - Checks Redis, database, and task registration

4. **backend/test_imports.py** (new)
   - Simple script to test imports

---

## 🎯 Quick Commands

### Clear Redis and Restart (if you see errors)
```bash
cd backend
python clear_redis.py
# Then restart Celery worker and FastAPI server
```

### Run Verification
```bash
cd backend
python verify_setup.py
```

### Test Imports
```bash
cd backend
python test_imports.py
```

---

## ✨ System Status

- ✅ **Circular Import**: FIXED
- ✅ **Task Registration**: WORKING  
- ✅ **API Server**: WORKING
- ✅ **Tests**: ALL 24 PASSING
- ✅ **Redis Integration**: WORKING

---

## 🎮 Try These Tasks

### CSV Processing (15 seconds)
```json
{
  "task_type": "csv_processing",
  "input_params": {
    "num_rows": 1000,
    "processing_time": 15
  }
}
```

### Email Sending (10 seconds)
```json
{
  "task_type": "email_sending",
  "input_params": {
    "num_emails": 10,
    "subject": "Test Email",
    "delay_per_email": 1.0
  }
}
```

### Image Processing (10 seconds)
```json
{
  "task_type": "image_processing",
  "input_params": {
    "num_images": 5,
    "target_width": 800,
    "target_height": 600
  }
}
```

---

## 📞 Need Help?

- See **TROUBLESHOOTING.md** for common issues
- See **README.md** for full documentation
- See **API_EXAMPLES.md** for more examples

**Everything is now working! Enjoy your Task Queue System!** 🎉

