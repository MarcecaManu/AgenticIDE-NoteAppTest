from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import json
import uuid
from datetime import datetime

from database import get_db, init_db, TaskModel
from schemas import TaskSubmit, TaskResponse, TaskList
from tasks import process_csv_data, send_emails, process_images
from celery_app import celery_app

app = FastAPI(title="Task Queue API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Task type mapping
TASK_FUNCTIONS = {
    "csv_processing": process_csv_data,
    "email_sending": send_emails,
    "image_processing": process_images
}


@app.post("/api/tasks/submit", response_model=TaskResponse)
async def submit_task(task_submit: TaskSubmit, db: Session = Depends(get_db)):
    """Submit a new background task"""
    
    # Validate task type
    if task_submit.task_type not in TASK_FUNCTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task type. Must be one of: {', '.join(TASK_FUNCTIONS.keys())}"
        )
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Create task record in database
    task = TaskModel(
        id=task_id,
        task_type=task_submit.task_type,
        status="PENDING",
        created_at=datetime.utcnow(),
        input_params=json.dumps(task_submit.input_params or {})
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # Submit task to Celery
    task_func = TASK_FUNCTIONS[task_submit.task_type]
    task_func.apply_async(args=[task_id, task_submit.input_params or {}])
    
    return task


@app.get("/api/tasks/", response_model=TaskList)
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    task_type: Optional[str] = Query(None, description="Filter by task type"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List all tasks with optional filters"""
    
    query = db.query(TaskModel)
    
    if status:
        query = query.filter(TaskModel.status == status)
    
    if task_type:
        query = query.filter(TaskModel.task_type == task_type)
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    tasks = query.order_by(TaskModel.created_at.desc()).offset(offset).limit(limit).all()
    
    return TaskList(tasks=tasks, total=total)


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db)):
    """Get specific task status and results"""
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db)):
    """Cancel a pending task"""
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only cancel if task is PENDING or RUNNING
    if task.status not in ["PENDING", "RUNNING"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task with status: {task.status}"
        )
    
    # Revoke task from Celery
    celery_app.control.revoke(task_id, terminate=True, signal='SIGKILL')
    
    # Update status in database
    task.status = "CANCELLED"
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Task cancelled successfully", "task_id": task_id}


@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str, db: Session = Depends(get_db)):
    """Retry a failed task"""
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Only retry FAILED or CANCELLED tasks
    if task.status not in ["FAILED", "CANCELLED"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot retry task with status: {task.status}. Only FAILED or CANCELLED tasks can be retried."
        )
    
    # Create new task ID for retry
    new_task_id = str(uuid.uuid4())
    
    # Parse input params
    input_params = json.loads(task.input_params) if task.input_params else {}
    
    # Create new task record
    new_task = TaskModel(
        id=new_task_id,
        task_type=task.task_type,
        status="PENDING",
        created_at=datetime.utcnow(),
        input_params=task.input_params
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Submit new task to Celery
    task_func = TASK_FUNCTIONS[task.task_type]
    task_func.apply_async(args=[new_task_id, input_params])
    
    return new_task


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Serve frontend
try:
    app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
except Exception:
    pass  # Frontend might not be available yet

