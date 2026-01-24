# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies

```powershell
pip install -r backend/requirements.txt
```

### Step 2: Start the Server

```powershell
python run.py
```

Or directly with uvicorn:

```powershell
uvicorn backend.main:app --reload
```

### Step 3: Open the Web Interface

Navigate to: **http://localhost:8000/**

## 📝 Try It Out

1. **Submit a Task**:
   - Select "Data Processing (CSV Analysis)"
   - Keep default parameters or customize them
   - Click "Submit Task"

2. **Watch Progress**:
   - Tasks update automatically every 2 seconds
   - Progress bars show completion percentage
   - Status badges show current state

3. **Manage Tasks**:
   - Click "Cancel" on running tasks
   - Click "Retry" on failed tasks
   - Use filters to find specific tasks

## 🧪 Run Tests

```powershell
pytest tests/ -v
```

Expected output: **20+ tests passed**

## 📊 API Documentation

Interactive API docs: **http://localhost:8000/docs**

## 🎯 Task Types to Try

### 1. Data Processing
- Analyzes CSV data
- Duration: 10-30 seconds
- Returns statistics (sum, average, min, max)

### 2. Email Simulation
- Simulates bulk email sending
- Configurable number and delay
- Shows success/failure counts

### 3. Image Processing
- Simulates image resize/conversion
- Multiple output formats
- Shows file size savings

## ⚡ Common Commands

**Start server**:
```powershell
python run.py
```

**Run tests**:
```powershell
pytest tests/ -v
```

**Run specific test**:
```powershell
pytest tests/test_task_queue.py::TestTaskSubmission -v
```

**View API docs**:
```
http://localhost:8000/docs
```

**View frontend**:
```
http://localhost:8000/
```

## 🔧 Configuration

All configuration is in `backend/main.py`:
- Storage path: `data/tasks.json` (auto-created)
- CORS: Enabled for all origins
- Auto-refresh: 2 seconds

## ❓ Need Help?

See [README.md](README.md) for full documentation.

---

**Happy task queuing! 🎉**
