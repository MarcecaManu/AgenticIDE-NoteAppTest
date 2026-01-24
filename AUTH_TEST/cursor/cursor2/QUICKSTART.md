# Quick Start Guide

## For Windows Users

### 1. Start the Backend
```cmd
start_backend.bat
```
This will:
- Create a virtual environment (if needed)
- Install all dependencies
- Start the FastAPI server on http://localhost:8000

### 2. Start the Frontend (in a new terminal)
```cmd
start_frontend.bat
```
This will start the frontend on http://localhost:8080

### 3. Run Tests (optional)
```cmd
run_tests.bat
```

## For Linux/Mac Users

### 1. Make scripts executable (first time only)
```bash
chmod +x start_backend.sh start_frontend.sh run_tests.sh
```

### 2. Start the Backend
```bash
./start_backend.sh
```

### 3. Start the Frontend (in a new terminal)
```bash
./start_frontend.sh
```

### 4. Run Tests (optional)
```bash
./run_tests.sh
```

## Manual Setup

If you prefer manual setup, see the detailed instructions in [README.md](README.md).

## Testing the Application

1. Open your browser to http://localhost:8080
2. Register a new account (username min 3 chars, password min 6 chars)
3. Login with your credentials
4. View your profile
5. Logout

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Troubleshooting

**Backend won't start:**
- Make sure Python 3.8+ is installed: `python --version`
- Check if port 8000 is already in use

**Frontend won't start:**
- Check if port 8080 is already in use
- Try a different port: `python -m http.server 3000`
- Update `API_BASE_URL` in `frontend/app.js` if you change the backend port

**CORS errors:**
- Make sure both backend and frontend are running
- Check that API_BASE_URL in frontend/app.js matches your backend URL

**Tests fail:**
- Make sure you're in the project root directory
- Ensure all dependencies are installed: `pip install -r backend/requirements.txt`

