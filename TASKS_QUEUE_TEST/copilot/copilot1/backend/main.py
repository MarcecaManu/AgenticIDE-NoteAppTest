"""FastAPI application for task queue system."""
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .models import TaskCreate, TaskResponse, TaskType, TaskStatus
from .storage import TaskStorage
from .task_queue import TaskQueue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize storage and task queue
storage = TaskStorage()
task_queue = TaskQueue(storage)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - startup and shutdown."""
    # Startup
    logger.info("Starting task queue worker...")
    await task_queue.start()
    yield
    # Shutdown
    logger.info("Stopping task queue worker...")
    await task_queue.stop()


# Create FastAPI app
app = FastAPI(
    title="Task Queue & Background Processing API",
    description="REST API for managing background tasks with real-time status updates",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/tasks/submit", response_model=TaskResponse, status_code=201)
async def submit_task(task_create: TaskCreate):
    """
    Submit a new background task.
    
    - **task_type**: Type of task (DATA_PROCESSING, EMAIL_SIMULATION, IMAGE_PROCESSING)
    - **parameters**: Optional parameters specific to the task type
    """
    try:
        task = await task_queue.submit_task(
            task_type=task_create.task_type,
            parameters=task_create.parameters
        )
        return task.to_response()
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/", response_model=List[TaskResponse])
async def get_all_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    task_type: Optional[TaskType] = Query(None, description="Filter by task type")
):
    """
    Get all tasks with optional filtering.
    
    - **status**: Filter by task status (PENDING, RUNNING, SUCCESS, FAILED, CANCELLED)
    - **task_type**: Filter by task type
    """
    try:
        tasks = task_queue.get_all_tasks()
        
        # Apply filters
        if status:
            tasks = [t for t in tasks if t.status == status]
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        # Sort by created_at descending (newest first)
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        
        return [task.to_response() for task in tasks]
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    """
    Get specific task status and results by ID.
    
    - **task_id**: Unique task identifier
    """
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_response()


@app.delete("/api/tasks/{task_id}", response_model=dict)
async def cancel_task(task_id: str):
    """
    Cancel a pending or running task.
    
    - **task_id**: Unique task identifier
    """
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatus.PENDING, TaskStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task.status}"
        )
    
    try:
        success = await task_queue.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=400, detail="Task could not be cancelled")
    except Exception as e:
        logger.error(f"Error cancelling task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error cancelling task: {str(e)}")
    
    return {"message": "Task cancelled successfully", "task_id": task_id}


@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse, status_code=201)
async def retry_task(task_id: str):
    """
    Retry a failed task by creating a new task with the same parameters.
    
    - **task_id**: Unique task identifier of the failed task
    """
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status != TaskStatus.FAILED:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed tasks. Current status: {task.status}"
        )
    
    new_task = await task_queue.retry_task(task_id)
    if not new_task:
        raise HTTPException(status_code=500, detail="Failed to retry task")
    
    return new_task.to_response()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "queue_running": task_queue._is_running,
        "total_tasks": len(task_queue.get_all_tasks())
    }


# Get the base directory (project root)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

# Mount static files for frontend
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


@app.get("/")
async def read_root():
    """Serve the frontend HTML page."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))
