# 🚀 Quick Start - Task Queue System

## Step 1: Install Backend Dependencies

Open a terminal and run:

```bash
cd backend
pip install fastapi uvicorn pydantic python-multipart
```

Or use the requirements file:

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Start the Backend Server

### Windows:
Double-click `start_backend.bat`

### Manual:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

## Step 3: Open the Frontend

### Option A: Direct File
Simply open `frontend/index.html` in your web browser

### Option B: HTTP Server (Recommended)
```bash
cd frontend
python -m http.server 8080
```

Then visit: `http://localhost:8080`

## Step 4: Try It Out!

1. **Submit a Data Processing Task**
   - Select "Data Processing" from the dropdown
   - Parameters are pre-filled: `{"rows": 1000}`
   - Click "Submit Task"
   - Watch it execute for ~10-15 seconds

2. **Submit an Email Simulation Task**
   - Select "Email Simulation"
   - Parameters: `{"recipients": ["user1@example.com", "user2@example.com"], "subject": "Test Email"}`
   - Click "Submit Task"
   - Watch it execute for ~4-6 seconds

3. **Submit an Image Processing Task**
   - Select "Image Processing"
   - Parameters: `{"images": ["image1.jpg", "image2.jpg", "image3.jpg"], "operation": "resize"}`
   - Click "Submit Task"
   - Watch it execute for ~6-9 seconds

4. **Explore Features**
   - Watch real-time progress bars
   - Filter tasks by status or type
   - Cancel a pending task
   - Let a task fail (or manually set one to FAILED in the JSON)
   - Retry a failed task
   - View detailed results

## Step 5: Run Tests (Optional)

```bash
cd tests
pip install pytest httpx
pytest test_tasks.py -v
```

Expected output:
```
test_tasks.py::test_submit_data_processing_task PASSED
test_tasks.py::test_submit_email_simulation_task PASSED
test_tasks.py::test_submit_image_processing_task PASSED
... (20+ tests)
===================== 20 passed in X.XXs =====================
```

## 🎯 What You'll See

### Backend Terminal
```
INFO:     127.0.0.1:XXXXX - "POST /api/tasks/submit HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /api/tasks/ HTTP/1.1" 200 OK
INFO:     127.0.0.1:XXXXX - "GET /api/tasks/{task_id} HTTP/1.1" 200 OK
```

### Frontend Interface
- **Statistics Dashboard**: Shows total, running, success, and failed task counts
- **Task Submission Form**: Easy-to-use form with example parameters
- **Task List**: Real-time updating list of all tasks
- **Progress Bars**: Visual progress indicators for running tasks
- **Status Colors**: Color-coded status badges (yellow=pending, blue=running, green=success, red=failed)

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Troubleshooting

### "Port 8000 is already in use"
```bash
# Find and kill the process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### "Module not found"
Make sure you installed dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### "CORS error in browser"
- Ensure backend is running on http://localhost:8000
- Check that CORS middleware is enabled in `backend/main.py`

### "Tasks not updating"
- Verify backend is running
- Check browser console (F12) for errors
- Frontend auto-refreshes every 2 seconds

## 📁 File Locations

- **Backend**: `backend/main.py`
- **Frontend**: `frontend/index.html`
- **Tests**: `tests/test_tasks.py`
- **Task Data**: `backend/tasks.json` (auto-generated)

## 🎨 Customization

### Change Task Duration
Edit `backend/main.py`:
- Data Processing: Line ~150 (`await asyncio.sleep(1.5)`)
- Email Simulation: Line ~190 (`await asyncio.sleep(2)`)
- Image Processing: Line ~220 (`await asyncio.sleep(3)`)

### Change Refresh Rate
Edit `frontend/index.html`:
- Line ~580: `refreshInterval = setInterval(refreshTasks, 2000);`
- Change `2000` to desired milliseconds

### Change Port
- Backend: Edit `start_backend.bat` or use `--port` flag
- Frontend: Edit `start_frontend.bat` or change port in command

## ✅ Success Checklist

- [ ] Backend dependencies installed
- [ ] Backend server running on port 8000
- [ ] Frontend opened in browser
- [ ] Can submit tasks
- [ ] Can see real-time updates
- [ ] Can cancel pending tasks
- [ ] Can retry failed tasks
- [ ] Tests pass successfully

## 🎓 Next Steps

1. Explore the API documentation at `/docs`
2. Run the test suite to see all features
3. Try different task parameters
4. Monitor the `backend/tasks.json` file
5. Read `README.md` for detailed documentation
6. Check `FEATURES.md` for complete feature list

## 💡 Tips

- Tasks auto-execute when submitted
- Progress updates every few seconds
- Task data persists across server restarts
- Use filters to find specific tasks
- Check browser DevTools Network tab to see API calls
- Backend logs show all requests

## 🚀 You're Ready!

The system is now running. Submit some tasks and watch them process in real-time!

For more details, see:
- `README.md` - Full documentation
- `SETUP.md` - Detailed setup guide
- `FEATURES.md` - Complete feature list
- `PROJECT_SUMMARY.md` - Project overview
