"""FastAPI backend application with REST API endpoints."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from pathlib import Path

from database import init_db, get_db_session
from models import Task, TaskStatus
from task_queue import task_queue


# Pydantic models for request/response
class TaskSubmitRequest(BaseModel):
    """Task submission request."""
    task_type: str
    params: dict = {}


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    task_type: str
    status: str
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    result_data: Optional[str]
    error_message: Optional[str]
    progress: float
    input_params: Optional[str]
    retry_count: int


# Create FastAPI app
app = FastAPI(title="Task Queue API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database and start task worker."""
    print("[Server] Startup event triggered")
    init_db()
    print("[Server] Database initialized")
    await task_queue.start_worker()
    print("[Server] Task worker started")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop task worker."""
    await task_queue.stop_worker()


@app.post("/api/tasks/submit", response_model=TaskResponse)
async def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db_session)):
    """
    Submit a new background task.
    
    Args:
        request: Task submission request
        db: Database session
        
    Returns:
        Created task
    """
    # Validate task type
    valid_types = ["DATA_PROCESSING", "EMAIL_SIMULATION", "IMAGE_PROCESSING"]
    if request.task_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid task type. Must be one of: {valid_types}")
    
    # Submit task to queue with database session
    task_id = await task_queue.submit_task(request.task_type, request.params, db)
    
    # Get created task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=500, detail="Failed to create task")
    
    return task.to_dict()


@app.get("/api/tasks/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    List all tasks with optional filtering.
    
    Args:
        status: Filter by status
        task_type: Filter by task type
        limit: Maximum number of tasks to return
        db: Database session
        
    Returns:
        List of tasks
    """
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    
    tasks = query.order_by(Task.created_at.desc()).limit(limit).all()
    return [task.to_dict() for task in tasks]


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db_session)):
    """
    Get specific task status and results.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        Task details
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task.to_dict()


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db_session)):
    """
    Cancel a pending task.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        Cancellation result
    """
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Try to cancel task
    success = await task_queue.cancel_task(task_id, db)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task.status}"
        )
    
    return {"message": "Task cancelled successfully", "task_id": task_id}


@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str, db: Session = Depends(get_db_session)):
    """
    Retry a failed task.
    
    Args:
        task_id: Task identifier
        db: Database session
        
    Returns:
        New task created for retry
    """
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Try to retry task
    new_task_id = await task_queue.retry_task(task_id, db)
    
    if not new_task_id:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry task with status: {task.status}. Only FAILED tasks can be retried."
        )
    
    # Get new task
    new_task = db.query(Task).filter(Task.id == new_task_id).first()
    return new_task.to_dict()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "queue_size": task_queue.queue.qsize()}


# Mount static files for frontend
# Get the directory of this file and go up one level to find frontend
current_file = Path(__file__).resolve()
backend_dir = current_file.parent
project_root = backend_dir.parent
frontend_dir = project_root / "frontend"

if frontend_dir.exists() and frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
