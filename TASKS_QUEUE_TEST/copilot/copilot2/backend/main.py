"""
FastAPI main application with REST API endpoints for task management.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import uuid
import json
from datetime import datetime

from backend.database import init_db, get_db, TaskDB
from backend.models import (
    TaskSubmitRequest, TaskResponse, TaskListResponse, 
    TaskRetryResponse, TaskStatus, TaskType
)
from backend.tasks import data_processing_task, email_simulation_task, image_processing_task

# Initialize FastAPI app
app = FastAPI(
    title="Task Queue & Background Processing System",
    description="Full-stack task queue system with FastAPI, Celery, and Redis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Task Queue & Background Processing System",
        "version": "1.0.0",
        "endpoints": {
            "submit_task": "POST /api/tasks/submit",
            "list_tasks": "GET /api/tasks/",
            "get_task": "GET /api/tasks/{task_id}",
            "delete_task": "DELETE /api/tasks/{task_id}",
            "retry_task": "POST /api/tasks/{task_id}/retry"
        }
    }


@app.post("/api/tasks/submit", response_model=TaskResponse)
def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit a new background task.
    
    Args:
        request: Task submission request with task_type and input_data/parameters
        db: Database session
        
    Returns:
        TaskResponse: Created task information
    """
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Get normalized input data
    input_data = request.get_input_data()
    
    # Create task record in database
    task_db = TaskDB(
        id=task_id,
        task_type=request.task_type,
        status=TaskStatus.PENDING.value,
        input_data=json.dumps(input_data),
        progress=0
    )
    db.add(task_db)
    db.commit()
    db.refresh(task_db)
    
    # Submit task to Celery based on task type
    task_map = {
        'data_processing': data_processing_task,
        'email_simulation': email_simulation_task,
        'image_processing': image_processing_task
    }
    
    celery_task = task_map[request.task_type]
    celery_task.apply_async(
        args=[task_id, input_data],
        task_id=task_id
    )
    
    return TaskResponse.from_orm(task_db)


@app.get("/api/tasks/", response_model=TaskListResponse)
def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering.
    
    Args:
        status: Optional status filter
        task_type: Optional task type filter
        limit: Maximum number of tasks to return
        offset: Offset for pagination
        db: Database session
        
    Returns:
        TaskListResponse: List of tasks and total count
    """
    query = db.query(TaskDB)
    
    # Apply filters
    if status:
        query = query.filter(TaskDB.status == status.upper())
    if task_type:
        query = query.filter(TaskDB.task_type == task_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    tasks = query.order_by(TaskDB.created_at.desc()).offset(offset).limit(limit).all()
    
    return TaskListResponse(
        tasks=[TaskResponse.from_orm(task) for task in tasks],
        total=total
    )


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, db: Session = Depends(get_db)):
    """
    Get specific task status and results.
    
    Args:
        task_id: Task ID
        db: Database session
        
    Returns:
        TaskResponse: Task information
    """
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse.from_orm(task)


@app.delete("/api/tasks/{task_id}")
def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """
    Cancel a pending or running task.
    
    Args:
        task_id: Task ID
        db: Database session
        
    Returns:
        dict: Cancellation status
    """
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatus.PENDING.value, TaskStatus.RUNNING.value]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel task with status {task.status}"
        )
    
    # Update task status to cancelled
    task.status = TaskStatus.CANCELLED.value
    task.completed_at = datetime.utcnow()
    task.error_message = "Task cancelled by user"
    db.commit()
    
    # Try to revoke the Celery task
    from backend.celery_app import celery_app
    celery_app.control.revoke(task_id, terminate=True)
    
    return {
        "message": "Task cancelled successfully",
        "task_id": task_id,
        "status": task.status
    }


@app.post("/api/tasks/{task_id}/retry", response_model=TaskRetryResponse)
def retry_task(task_id: str, db: Session = Depends(get_db)):
    """
    Retry a failed task.
    
    Args:
        task_id: Task ID of the failed task
        db: Database session
        
    Returns:
        TaskRetryResponse: New task ID and message
    """
    original_task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    
    if not original_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if original_task.status != TaskStatus.FAILED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed tasks. Current status: {original_task.status}"
        )
    
    # Create new task with same parameters
    new_task_id = str(uuid.uuid4())
    input_data = json.loads(original_task.input_data) if original_task.input_data else {}
    
    new_task_db = TaskDB(
        id=new_task_id,
        task_type=original_task.task_type,
        status=TaskStatus.PENDING.value,
        input_data=original_task.input_data,
        progress=0
    )
    db.add(new_task_db)
    db.commit()
    
    # Submit new task to Celery
    task_map = {
        'data_processing': data_processing_task,
        'email_simulation': email_simulation_task,
        'image_processing': image_processing_task
    }
    
    celery_task = task_map[original_task.task_type]
    celery_task.apply_async(
        args=[new_task_id, input_data],
        task_id=new_task_id
    )
    
    return TaskRetryResponse(
        new_task_id=new_task_id,
        message=f"Task retry submitted. Original task: {task_id}, New task: {new_task_id}"
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
