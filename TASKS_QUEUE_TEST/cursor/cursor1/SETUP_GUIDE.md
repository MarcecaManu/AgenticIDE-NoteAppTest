# Quick Setup Guide

## 1. Install Redis

### Windows:
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

### macOS:
```bash
brew install redis
brew services start redis
```

### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis
```

## 2. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 3. Start Services

### Terminal 1: Start Redis (if not running as service)
```bash
redis-server
```

### Terminal 2: Start Celery Worker
```bash
cd backend

# Windows
celery -A celery_app worker --loglevel=info --pool=solo

# macOS/Linux
celery -A celery_app worker --loglevel=info
```

### Terminal 3: Start FastAPI Server
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 4. Open Browser

Navigate to: http://localhost:8000

## 5. Run Tests (Optional)

```bash
cd tests
pytest -v
```

## Quick Start Scripts

### Windows:
```bash
# Terminal 1
cd backend
start_celery.bat

# Terminal 2
cd backend
start_server.bat
```

### macOS/Linux:
```bash
# Terminal 1
cd backend
chmod +x start_celery.sh
./start_celery.sh

# Terminal 2
cd backend
chmod +x start_server.sh
./start_server.sh
```

## Verify Installation

1. Open http://localhost:8000 in your browser
2. Select "CSV Data Processing" task type
3. Click "Submit Task"
4. Watch the task progress in real-time

## Troubleshooting

**Redis not connecting?**
- Check if Redis is running: `redis-cli ping` (should return "PONG")
- Verify Redis is on port 6379

**Celery worker errors?**
- On Windows, always use `--pool=solo` flag
- Ensure all dependencies installed: `pip install -r requirements.txt`

**Tasks not executing?**
- Check Celery worker is running (Terminal 2)
- Look for errors in Celery worker terminal
- Verify Redis connection

**Frontend not loading?**
- Ensure FastAPI server is running (Terminal 3)
- Check http://localhost:8000/api/health

## Next Steps

1. Submit different types of tasks
2. Monitor task progress
3. Try cancelling and retrying tasks
4. Filter tasks by status or type
5. Click on tasks to view detailed information

Enjoy your Task Queue System! 🚀

