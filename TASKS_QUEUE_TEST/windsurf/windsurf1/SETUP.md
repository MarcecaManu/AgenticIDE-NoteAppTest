# Quick Setup Guide

## Prerequisites
- Python 3.8 or higher
- Web browser (Chrome, Firefox, Safari, or Edge)

## Installation Steps

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
The API will be available at `http://localhost:8000`

**Start Frontend:**
```bash
start_frontend.bat
```
Then open `http://localhost:8080` in your browser

**Run Tests:**
```bash
run_tests.bat
```

### Option 2: Manual Commands

**Start Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Start Frontend:**
Open `frontend/index.html` directly in your browser, or serve it:
```bash
cd frontend
python -m http.server 8080
```

**Run Tests:**
```bash
cd tests
pytest test_tasks.py -v
```

## First Steps

1. Start the backend server
2. Open the frontend in your browser
3. Try submitting different task types:
   - **Data Processing**: Analyzes data rows (10-15 seconds)
   - **Email Simulation**: Simulates sending emails (4-6 seconds)
   - **Image Processing**: Simulates image operations (6-9 seconds)
4. Watch tasks execute in real-time with progress updates
5. Try cancelling pending tasks or retrying failed tasks

## API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Troubleshooting

**Port already in use:**
- Change the port in `start_backend.bat` or `start_frontend.bat`
- Or kill the process using the port

**Module not found:**
- Make sure you installed dependencies: `pip install -r requirements.txt`

**CORS errors:**
- Ensure backend is running on `http://localhost:8000`
- Check browser console for specific errors

**Tasks not updating:**
- Check backend logs for errors
- Verify the frontend is polling the API (check Network tab in browser DevTools)

## Project Structure
```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Backend dependencies
│   └── tasks.json          # Task storage (auto-generated)
├── frontend/
│   └── index.html          # Frontend application
├── tests/
│   ├── test_tasks.py       # Test suite (20+ tests)
│   └── requirements.txt    # Test dependencies
├── start_backend.bat       # Backend startup script
├── start_frontend.bat      # Frontend startup script
├── run_tests.bat          # Test runner script
├── README.md              # Full documentation
└── SETUP.md              # This file
```

## Testing

The test suite includes 20+ comprehensive tests covering:
- Task submission for all task types
- Task listing and filtering
- Task cancellation and retry logic
- Task execution and progress tracking
- Error handling and edge cases
- Persistent storage verification

Run tests with:
```bash
cd tests
pytest test_tasks.py -v
```

For more detailed output:
```bash
pytest test_tasks.py -v -s
```

## Next Steps

After setup, explore:
1. Submit tasks with different parameters
2. Monitor real-time progress updates
3. Filter tasks by status or type
4. View detailed task results
5. Test cancellation and retry features
6. Check the API documentation at `/docs`
