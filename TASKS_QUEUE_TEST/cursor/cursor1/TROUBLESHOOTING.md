# Troubleshooting Guide

## Issue: "Received unregistered task" Error

### Symptoms
```
KeyError: 'backend.tasks.data_processing_task'
[ERROR] Received unregistered task of type 'backend.tasks.data_processing_task'.
The message has been ignored and discarded.
```

### Root Cause
- Tasks are not properly registered with Celery worker
- Old task messages with wrong names in Redis queue

### Solution

**Step 1: Stop all running services**
- Stop Celery worker (Ctrl+C in its terminal)
- Stop FastAPI server (Ctrl+C in its terminal)  
- Redis can keep running

**Step 2: Clear Redis queue**

Option A - Using the clear script:
```bash
cd backend
python clear_redis.py
```

Option B - Using redis-cli:
```bash
redis-cli FLUSHDB
```

Option C - Using Python:
```bash
cd backend
python -c "import redis; r=redis.Redis(); r.flushdb(); print('Redis cleared')"
```

**Step 3: Verify setup**
```bash
cd backend
python verify_setup.py
```

This will check:
- All imports work correctly
- Redis is accessible
- Database is initialized
- Celery tasks are registered

**Step 4: Restart Celery worker**

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

Look for this in the output:
```
[tasks]
  . tasks.process_csv_data
  . tasks.send_emails
  . tasks.process_images
```

✅ If you see these 3 tasks, the worker is configured correctly!

**Step 5: Restart FastAPI server**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 6: Test the system**

Visit http://localhost:8000 and submit a task. It should work now!

---

## Other Common Issues

### Issue: "Cannot connect to Redis"

**Error:**
```
[ERROR] Consumer: Cannot connect to redis://localhost:6379/0
```

**Solution:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start it
redis-server

# Or on macOS
brew services start redis

# Or on Linux
sudo systemctl start redis
```

### Issue: "ModuleNotFoundError: No module named 'celery_app'"

**Solution:**
Make sure you're in the `backend/` directory:
```bash
cd backend
celery -A celery_app worker --loglevel=info --pool=solo
```

### Issue: "Tasks stay in PENDING forever"

**Symptoms:**
- Tasks are submitted successfully
- They show status "PENDING" 
- Never change to "RUNNING"

**Root Cause:**
Celery worker is not running or not connected

**Solution:**
1. Check Celery worker terminal for errors
2. Make sure Redis is running (`redis-cli ping`)
3. Restart Celery worker
4. Check worker logs for "Connected to redis" message

### Issue: "Port 8000 already in use"

**Error:**
```
[ERROR] [Errno 48] Address already in use
```

**Solution:**

Option A - Use different port:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

Then update `frontend/app.js`:
```javascript
const API_BASE = 'http://localhost:8001/api';
```

Option B - Kill process using port 8000:

**Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: "Database locked" error

**Error:**
```
sqlite3.OperationalError: database is locked
```

**Solution:**
```bash
cd backend
rm tasks.db
python -c "from database import init_db; init_db(); print('Database recreated')"
```

### Issue: Tasks fail immediately

**Check Celery worker logs** for the actual error. Common causes:

1. **Missing dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Import errors:**
```bash
cd backend
python verify_setup.py
```

3. **Database issues:**
```bash
cd backend
python -c "from database import init_db; init_db()"
```

---

## Verification Checklist

Run through this checklist to ensure everything is set up correctly:

### 1. Redis
- [ ] Redis is installed
- [ ] Redis is running (`redis-cli ping` returns PONG)
- [ ] Can connect to redis://localhost:6379/0

### 2. Python Dependencies
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Virtual environment activated (optional but recommended)
- [ ] All packages installed (`pip install -r backend/requirements.txt`)

### 3. Database
- [ ] Database file exists or will be created automatically
- [ ] Can import database module (`python -c "from database import init_db"`)

### 4. Celery
- [ ] Celery worker starts without errors
- [ ] Three tasks are registered (check worker output)
- [ ] Worker is connected to Redis

### 5. FastAPI
- [ ] Server starts without errors
- [ ] Can access http://localhost:8000
- [ ] API health check works: http://localhost:8000/api/health

### 6. Frontend
- [ ] Can load http://localhost:8000
- [ ] Can see the task submission form
- [ ] No errors in browser console (F12)

---

## Fresh Start (Nuclear Option)

If nothing else works, start completely fresh:

```bash
# 1. Stop everything
# Press Ctrl+C in all terminals

# 2. Clear Redis
redis-cli FLUSHDB

# 3. Remove database
cd backend
rm -f tasks.db test.db

# 4. Remove Python cache
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 5. Reinstall dependencies
pip install -r requirements.txt

# 6. Verify setup
python verify_setup.py

# 7. Start Redis
redis-server

# 8. Start Celery worker (new terminal)
celery -A celery_app worker --loglevel=info --pool=solo

# 9. Start FastAPI (new terminal)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 10. Open browser
# http://localhost:8000
```

---

## Getting Help

If you're still having issues:

1. Check the Celery worker logs (terminal where worker is running)
2. Check the FastAPI server logs (terminal where uvicorn is running)
3. Check browser console (F12 → Console tab)
4. Run `python verify_setup.py` to check configuration
5. Review the error messages carefully

### Useful Debug Commands

**Check what tasks are registered:**
```bash
cd backend
python -c "from celery_app import celery_app; print(list(celery_app.tasks.keys()))"
```

**Test database connection:**
```bash
cd backend
python -c "from database import SessionLocal; db=SessionLocal(); print('DB OK'); db.close()"
```

**Test Redis connection:**
```bash
redis-cli ping
redis-cli INFO
```

**Test API:**
```bash
curl http://localhost:8000/api/health
```

**Submit test task:**
```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"task_type": "csv_processing", "input_params": {"num_rows": 100, "processing_time": 5}}'
```

---

## Prevention

To avoid these issues in the future:

1. **Always run commands from the `backend/` directory**
2. **Clear Redis queue when making changes to task definitions**
3. **Restart Celery worker after code changes**
4. **Check that all three services are running** (Redis, Celery, FastAPI)
5. **Use the verify_setup.py script** before starting

---

## Still Not Working?

Make sure:
- You're in the correct directory (`backend/`)
- Redis is actually running (not just installed)
- No firewall blocking localhost:6379 or localhost:8000
- Python version is 3.8 or higher
- All dependencies are installed
- No other application using ports 6379 or 8000

