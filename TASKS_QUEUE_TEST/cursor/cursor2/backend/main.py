"""
FastAPI backend server
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from backend.database import init_db, get_db_session
from backend.models import Task
from backend.task_queue import task_queue


# Request/Response models
class TaskSubmitRequest(BaseModel):
    task_type: str
    parameters: Optional[Dict[str, Any]] = {}


class TaskResponse(BaseModel):
    id: str
    task_type: str
    status: str
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    result_data: Optional[str]
    error_message: Optional[str]
    progress: float
    parameters: Optional[str]


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    await task_queue.start()
    yield
    # Shutdown
    await task_queue.stop()


# Create FastAPI app
app = FastAPI(
    title="Task Queue API",
    description="Background task processing system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints
@app.post("/api/tasks/submit", response_model=TaskResponse, status_code=201)
async def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db_session)):
    """Submit a new background task"""
    # Normalize task type to lowercase for consistency
    task_type_normalized = request.task_type.lower()
    
    if task_type_normalized not in ["data_processing", "email_simulation", "image_processing"]:
        raise HTTPException(status_code=400, detail="Invalid task type")
    
    task_id = await task_queue.submit_task(task_type_normalized, request.parameters)
    
    # Retrieve and return the created task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=500, detail="Task created but not found")
    
    return TaskResponse(**task.to_dict())


@app.get("/api/tasks/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db_session)
):
    """List all tasks with optional filtering"""
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if task_type:
        query = query.filter(Task.task_type == task_type)
    
    tasks = query.order_by(Task.created_at.desc()).all()
    return [TaskResponse(**task.to_dict()) for task in tasks]


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db_session)):
    """Get specific task status and results"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskResponse(**task.to_dict())


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db_session)):
    """Cancel a pending task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    success = await task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be cancelled (already completed or failed)"
        )
    
    return {"status": "cancelled", "task_id": task_id}


@app.post("/api/tasks/{task_id}/retry")
async def retry_task(task_id: str, db: Session = Depends(get_db_session)):
    """Retry a failed task"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    new_task_id = await task_queue.retry_task(task_id)
    if not new_task_id:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be retried (not in FAILED status)"
        )
    
    return {"status": "retried", "new_task_id": new_task_id}


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Serve frontend static files
try:
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
except Exception:
    pass  # Frontend directory might not exist yet


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

