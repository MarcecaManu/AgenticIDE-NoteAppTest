# Task Queue & Background Processing System

A full-stack task queue and background processing system built with FastAPI backend and vanilla HTML/JavaScript frontend. Supports multiple task types with real-time status monitoring, progress tracking, and persistent storage.

## 🚀 Features

### Backend
- **FastAPI REST API** with 5 endpoints for complete task lifecycle management
- **Asyncio-based task queue** for efficient background processing
- **SQLite database** for persistent task storage
- **Real-time progress tracking** for long-running tasks
- **Three task types**:
  - Data Processing (CSV analysis simulation)
  - Email Simulation (bulk email sending)
  - Image Processing (resize/convert operations)

### Frontend
- **Clean, modern UI** with gradient design
- **Real-time updates** every 2 seconds
- **Filter/search** tasks by status or type
- **Submit tasks** with custom parameters
- **Monitor progress** with visual progress bars
- **Cancel pending tasks** before execution
- **Retry failed tasks** with automatic retry tracking

### Task Management
- **5 Task Statuses**: PENDING, RUNNING, SUCCESS, FAILED, CANCELLED
- **Comprehensive tracking**: creation time, start time, completion time, progress percentage
- **Error handling**: detailed error messages for failed tasks
- **Retry mechanism**: retry failed tasks with automatic retry count

## 📁 Project Structure

```
copilot3/
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & REST endpoints
│   ├── models.py            # SQLAlchemy database models
│   ├── database.py          # Database configuration
│   ├── task_queue.py        # Asyncio task queue manager
│   └── task_handlers.py     # Task type implementations
├── frontend/
│   └── index.html           # Single-page application
├── tests/
│   ├── __init__.py
│   └── test_api.py          # 16 automated tests
├── requirements.txt
└── README.md
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or navigate to the project directory**
```powershell
cd c:\Users\marce\Desktop\Tesi\AgenticIDE-NoteAppTest\TASKS_QUEUE_TEST\copilot\copilot3
```

2. **Create a virtual environment (recommended)**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

3. **Install dependencies**
```powershell
pip install -r requirements.txt
```

## 🚀 Running the Application

### Start the Backend Server

**Option 1: Using the start script (recommended)**
```powershell
.\start.bat
```

**Option 2: Manual start**
```powershell
cd backend
python run_server.py
```

**Option 3: Using uvicorn directly**
```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

### Access the Frontend

Open your web browser and navigate to:
```
http://localhost:8000
```

The frontend is automatically served by FastAPI from the `frontend/` directory.

## 📡 API Endpoints

### 1. Submit Task
```http
POST /api/tasks/submit
Content-Type: application/json

{
  "task_type": "DATA_PROCESSING",
  "params": {
    "file_size": 1000,
    "complexity": "medium"
  }
}
```

### 2. List Tasks
```http
GET /api/tasks/
GET /api/tasks/?status=PENDING
GET /api/tasks/?task_type=DATA_PROCESSING
GET /api/tasks/?status=SUCCESS&task_type=EMAIL_SIMULATION
```

### 3. Get Specific Task
```http
GET /api/tasks/{task_id}
```

### 4. Cancel Task
```http
DELETE /api/tasks/{task_id}
```

### 5. Retry Failed Task
```http
POST /api/tasks/{task_id}/retry
```

### 6. Health Check
```http
GET /api/health
```

## 🎯 Task Types & Parameters

### Data Processing
Simulates CSV file analysis (10-30 seconds).

**Parameters:**
```json
{
  "file_size": 1000,        // Number of rows (default: 1000)
  "complexity": "medium"     // "low", "medium", or "high" (default: "medium")
}
```

**Results:**
- Rows processed
- Columns analyzed
- Null values found
- Summary statistics (mean, median, std_dev)

### Email Simulation
Simulates bulk email sending with random failures.

**Parameters:**
```json
{
  "recipient_count": 10,    // Number of recipients (default: 10)
  "template": "welcome"      // Email template name (default: "default")
}
```

**Results:**
- Total recipients
- Successfully sent count
- Failed count
- Send rate

### Image Processing
Simulates image resize/conversion operations.

**Parameters:**
```json
{
  "image_count": 5,         // Number of images (default: 5)
  "operation": "resize",     // Operation type (default: "resize")
  "target_size": "1920x1080" // Target dimensions (default: "1920x1080")
}
```

**Results:**
- Processed images list
- File sizes
- Operation details

## 🧪 Running Tests

The project includes 16 comprehensive automated tests covering:
- Task submission for all task types
- Status filtering and searching
- Task cancellation
- Task retry logic
- Error handling
- Invalid input validation

### Run All Tests
```powershell
cd tests
pytest test_api.py -v
```

### Run Specific Test
```powershell
pytest test_api.py::test_submit_data_processing_task -v
```

### Test Coverage
- ✅ Health check endpoint
- ✅ Submit all task types (DATA_PROCESSING, EMAIL_SIMULATION, IMAGE_PROCESSING)
- ✅ Invalid task type handling
- ✅ List all tasks
- ✅ Filter tasks by status
- ✅ Filter tasks by type
- ✅ Get specific task by ID
- ✅ Get nonexistent task (404 error)
- ✅ Cancel pending task
- ✅ Cancel nonexistent task
- ✅ Task execution success
- ✅ Retry failed task
- ✅ Retry non-failed task (error handling)
- ✅ Input parameters storage

## 🎨 Frontend Features

### Submit Tasks
1. Select task type from dropdown
2. Enter JSON parameters (examples provided)
3. Click "Submit Task"
4. Receive confirmation notification

### Monitor Tasks
- **Real-time updates** every 2 seconds
- **Visual progress bars** for running tasks
- **Status badges** with color coding
- **Detailed information** including timestamps, retry count
- **Results display** for successful tasks
- **Error messages** for failed tasks

### Filter Tasks
- Filter by **status**: All, Pending, Running, Success, Failed, Cancelled
- Filter by **type**: All, Data Processing, Email Simulation, Image Processing
- Combine filters for precise results

### Task Actions
- **Cancel**: Stop pending or running tasks
- **Retry**: Restart failed tasks with same parameters

## 💾 Database

The application uses SQLite for persistent storage:
- Database file: `backend/tasks.db`
- Automatically created on first run
- All task data persists across server restarts

### Database Schema

**tasks** table:
- `id` (String): Unique task identifier (UUID)
- `task_type` (String): Type of task
- `status` (String): Current status
- `created_at` (DateTime): Task creation timestamp
- `started_at` (DateTime): Task start timestamp
- `completed_at` (DateTime): Task completion timestamp
- `result_data` (Text): JSON result data
- `error_message` (Text): Error message if failed
- `progress` (Float): Progress percentage (0-100)
- `input_params` (Text): JSON input parameters
- `retry_count` (Integer): Number of times retried

## 🔧 Configuration

### Change Server Port
Edit `backend/main.py`:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)  # Change port here
```

### Adjust Auto-Refresh Interval
Edit `frontend/index.html`:
```javascript
// Change refresh interval (in milliseconds)
autoRefreshInterval = setInterval(() => {
    loadTasks();
}, 3000);  // Change from 2000 to 3000 for 3-second refresh
```

### Modify Task Duration
Edit task handlers in `backend/task_handlers.py`:
```python
# In data_processing_task function
duration_map = {"low": 5, "medium": 10, "high": 20}  # Adjust durations
```

## 🐛 Troubleshooting

### Database Lock Error
If you encounter database lock errors:
```powershell
# Stop the server
# Delete the database file
rm backend/tasks.db
# Restart the server
```

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Import Errors
Ensure all dependencies are installed:
```powershell
pip install -r requirements.txt
```

## 📊 System Architecture

```
┌─────────────┐
│   Frontend  │ (HTML/JavaScript)
│  index.html │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────┐
│   FastAPI   │ (main.py)
│  REST API   │
└──────┬──────┘
       │
   ┌───┴───┬─────────┐
   │       │         │
┌──▼──┐ ┌──▼──┐  ┌──▼──────┐
│ DB  │ │Queue│  │ Workers │
│SQLite│ │asyncio│ │handlers│
└─────┘ └─────┘  └─────────┘
```

## 🎯 Key Design Decisions

1. **Asyncio over Celery**: Simpler setup, no Redis dependency, suitable for single-machine deployments
2. **SQLite**: Lightweight, file-based, perfect for development and small-scale production
3. **Vanilla JavaScript**: No framework dependencies, faster load times, easier to understand
4. **Real-time polling**: Simple 2-second polling instead of WebSockets for real-time updates
5. **In-memory queue**: Fast task submission and processing without external message brokers

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

This is a demonstration project. Feel free to fork and modify for your needs.

## 📧 Support

For issues or questions, please check the troubleshooting section or review the test suite for usage examples.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern web technologies**
