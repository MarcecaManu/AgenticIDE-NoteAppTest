# Installation & Setup Instructions

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8 or higher installed
- ✅ pip (Python package manager)
- ✅ PowerShell or Command Prompt

## Step-by-Step Installation

### 1. Navigate to Project Directory

```powershell
cd c:\Users\marce\Desktop\Tesi\AgenticIDE-NoteAppTest\TASKS_QUEUE_TEST\copilot\copilot1
```

### 2. Install Python Dependencies

```powershell
pip install -r backend/requirements.txt
```

**Expected packages to be installed:**
- fastapi==0.109.0
- uvicorn==0.27.0
- pydantic==2.5.3
- pytest==7.4.4
- pytest-asyncio==0.23.3
- httpx==0.26.0

### 3. Verify Installation

Run the following to check if packages are installed:

```powershell
python -c "import fastapi; import uvicorn; import pydantic; print('All packages installed successfully!')"
```

### 4. Start the Application

**Option A - Using run.py (Recommended):**
```powershell
python run.py
```

**Option B - Using uvicorn directly:**
```powershell
uvicorn backend.main:app --reload
```

**Expected Output:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Starting task queue worker...
INFO:     Task queue worker started
INFO:     Application startup complete.
```

### 5. Access the Application

Open your browser and navigate to:
- **Web Interface**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

### 6. Run Tests (Optional)

In a **new PowerShell window**:

```powershell
cd c:\Users\marce\Desktop\Tesi\AgenticIDE-NoteAppTest\TASKS_QUEUE_TEST\copilot\copilot1
pytest tests/ -v
```

**Expected Output:**
- 24 tests should pass
- Test coverage includes all major features

## Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```powershell
pip install --upgrade -r backend/requirements.txt
```

### Issue: Port 8000 already in use

**Solution 1 - Stop other process:**
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution 2 - Use different port:**
```powershell
uvicorn backend.main:app --reload --port 8001
```
Then update API_BASE in `frontend/app.js` to `http://localhost:8001/api`

### Issue: Permission denied when creating data folder

**Solution:**
```powershell
# Create data folder manually with appropriate permissions
mkdir data -ErrorAction SilentlyContinue
```

### Issue: Tests fail with "RuntimeError: Event loop is closed"

**Solution:**
This is a known issue with pytest-asyncio. Update pytest.ini if needed, or run:
```powershell
pytest tests/ -v --asyncio-mode=auto
```

### Issue: CORS errors in browser

**Solution:**
Make sure you're accessing via `http://localhost:8000` and not opening the HTML file directly.

## Verification Checklist

After installation, verify:

- [ ] Server starts without errors
- [ ] Can access web interface at http://localhost:8000/
- [ ] Can access API docs at http://localhost:8000/docs
- [ ] Can submit a task through the web interface
- [ ] Tasks appear in the task list
- [ ] Progress updates automatically
- [ ] Can cancel a task
- [ ] Can view task results
- [ ] Tests pass (optional but recommended)

## Next Steps

Once installed and verified:

1. **Explore the Web Interface**: Submit different task types and watch them execute
2. **Try the API**: Use the interactive docs at `/docs` to test endpoints
3. **Review the Code**: Check out the well-documented source files
4. **Run Tests**: Verify everything works with the test suite
5. **Customize**: Modify task parameters and behavior

## Additional Resources

- **Full Documentation**: See [README.md](README.md)
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Project Summary**: See [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## Support

If you encounter issues:
1. Check the console/terminal output for error messages
2. Review the troubleshooting section above
3. Verify all dependencies are installed correctly
4. Check that Python version is 3.8 or higher

---

**Installation complete! Ready to process tasks! 🚀**
