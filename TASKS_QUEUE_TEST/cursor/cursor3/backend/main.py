"""FastAPI main application with REST API endpoints."""
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import os

from database import init_db, get_db, Task
import task_queue as tq_module

# Initialize FastAPI app
app = FastAPI(title="Task Queue & Background Processing System")


def get_task_queue():
    """Dependency to get the task queue instance."""
    return tq_module.task_queue

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend files
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


# Pydantic models for request/response
class TaskSubmitRequest(BaseModel):
    task_type: str
    parameters: Optional[Dict[str, Any]] = {}


class TaskResponse(BaseModel):
    id: str
    task_type: str
    status: str
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    result_data: Optional[Dict[str, Any]]
    error_message: Optional[str]
    progress: Optional[str]
    parameters: Optional[Dict[str, Any]]


@app.on_event("startup")
async def startup_event():
    """Initialize database and start task queue on startup."""
    init_db()
    tq_module.task_queue.start()


@app.get("/")
async def read_root():
    """Serve the frontend index.html."""
    frontend_file = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_file):
        return FileResponse(frontend_file)
    return {"message": "Task Queue System API - Frontend not found"}


@app.get("/styles.css")
async def get_styles():
    """Serve styles.css."""
    css_file = os.path.join(frontend_path, "styles.css")
    if os.path.exists(css_file):
        return FileResponse(css_file, media_type="text/css")
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/app.js")
async def get_app_js():
    """Serve app.js."""
    js_file = os.path.join(frontend_path, "app.js")
    if os.path.exists(js_file):
        return FileResponse(js_file, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="File not found")


@app.post("/api/tasks/submit", response_model=TaskResponse)
async def submit_task(request: TaskSubmitRequest, db: Session = Depends(get_db), 
                     task_queue = Depends(get_task_queue)):
    """Submit a new background task."""
    try:
        task_id = task_queue.submit_task(request.task_type, request.parameters or {})
        task = task_queue.get_task(task_id, db)
        if not task:
            raise HTTPException(status_code=500, detail="Failed to create task")
        return task.to_dict()
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/tasks/", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    task_queue = Depends(get_task_queue)
):
    """List all tasks with optional filtering by status and type."""
    try:
        tasks = task_queue.get_all_tasks(db, status, task_type)
        return [task.to_dict() for task in tasks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: Session = Depends(get_db),
                  task_queue = Depends(get_task_queue)):
    """Get specific task status and results."""
    task = task_queue.get_task(task_id, db)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str, db: Session = Depends(get_db),
                     task_queue = Depends(get_task_queue)):
    """Cancel a pending or running task."""
    success = task_queue.cancel_task(task_id, db)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"message": "Task cancelled successfully", "task_id": task_id}


@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str, db: Session = Depends(get_db),
                    task_queue = Depends(get_task_queue)):
    """Retry a failed task."""
    new_task_id = task_queue.retry_task(task_id, db)
    if not new_task_id:
        raise HTTPException(status_code=400, detail="Task cannot be retried")
    
    new_task = task_queue.get_task(new_task_id, db)
    return new_task.to_dict()


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Task Queue System is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

