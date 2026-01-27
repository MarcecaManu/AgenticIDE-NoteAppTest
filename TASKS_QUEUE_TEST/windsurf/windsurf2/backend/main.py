from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from enum import Enum
from contextlib import asynccontextmanager
import asyncio
import uuid
import json
import os
from pathlib import Path
import random
import time

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskType(str, Enum):
    DATA_PROCESSING = "data_processing"
    EMAIL_SIMULATION = "email_simulation"
    IMAGE_PROCESSING = "image_processing"

class TaskSubmitRequest(BaseModel):
    task_type: TaskType
    parameters: Optional[Dict[str, Any]] = {}

class Task(BaseModel):
    id: str
    task_type: TaskType
    status: TaskStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: int = 0
    parameters: Optional[Dict[str, Any]] = {}

STORAGE_FILE = Path("backend/tasks_data.json")
tasks_db: Dict[str, Task] = {}
task_queue: asyncio.Queue = asyncio.Queue()
worker_task: Optional[asyncio.Task] = None

def load_tasks():
    global tasks_db
    if STORAGE_FILE.exists():
        try:
            with open(STORAGE_FILE, 'r') as f:
                data = json.load(f)
                tasks_db = {task_id: Task(**task_data) for task_id, task_data in data.items()}
        except Exception as e:
            print(f"Error loading tasks: {e}")
            tasks_db = {}
    else:
        tasks_db = {}

def save_tasks():
    STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_FILE, 'w') as f:
        json.dump({task_id: task.model_dump() for task_id, task in tasks_db.items()}, f, indent=2)

async def data_processing_task(task_id: str, parameters: Dict[str, Any]):
    task = tasks_db[task_id]
    rows = parameters.get("rows", 1000)
    
    await asyncio.sleep(1)
    task.progress = 10
    save_tasks()
    
    results = {
        "total_rows": rows,
        "processed": 0,
        "statistics": {}
    }
    
    for i in range(10):
        if task.status == TaskStatus.CANCELLED:
            raise Exception("Task was cancelled")
        
        await asyncio.sleep(random.uniform(1, 3))
        task.progress = 10 + (i + 1) * 9
        results["processed"] = int(rows * (i + 1) / 10)
        save_tasks()
    
    results["statistics"] = {
        "mean": random.uniform(50, 150),
        "median": random.uniform(40, 160),
        "std_dev": random.uniform(10, 30),
        "min": random.uniform(0, 50),
        "max": random.uniform(150, 200)
    }
    
    return results

async def email_simulation_task(task_id: str, parameters: Dict[str, Any]):
    task = tasks_db[task_id]
    recipient_count = parameters.get("recipient_count", 10)
    
    results = {
        "total_emails": recipient_count,
        "sent": 0,
        "failed": 0,
        "recipients": []
    }
    
    for i in range(recipient_count):
        if task.status == TaskStatus.CANCELLED:
            raise Exception("Task was cancelled")
        
        await asyncio.sleep(random.uniform(0.5, 2))
        
        success = random.random() > 0.1
        recipient = f"user{i+1}@example.com"
        
        if success:
            results["sent"] += 1
            results["recipients"].append({"email": recipient, "status": "sent"})
        else:
            results["failed"] += 1
            results["recipients"].append({"email": recipient, "status": "failed"})
        
        task.progress = int((i + 1) / recipient_count * 100)
        save_tasks()
    
    return results

async def image_processing_task(task_id: str, parameters: Dict[str, Any]):
    task = tasks_db[task_id]
    image_count = parameters.get("image_count", 5)
    operation = parameters.get("operation", "resize")
    
    results = {
        "total_images": image_count,
        "processed": 0,
        "operation": operation,
        "images": []
    }
    
    for i in range(image_count):
        if task.status == TaskStatus.CANCELLED:
            raise Exception("Task was cancelled")
        
        await asyncio.sleep(random.uniform(2, 4))
        
        image_result = {
            "filename": f"image_{i+1}.jpg",
            "original_size": f"{random.randint(1920, 3840)}x{random.randint(1080, 2160)}",
            "processed_size": f"{random.randint(800, 1920)}x{random.randint(600, 1080)}",
            "file_size_mb": round(random.uniform(0.5, 5.0), 2)
        }
        
        results["processed"] += 1
        results["images"].append(image_result)
        
        task.progress = int((i + 1) / image_count * 100)
        save_tasks()
    
    return results

async def execute_task(task_id: str):
    task = tasks_db[task_id]
    
    try:
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(timezone.utc).isoformat()
        task.progress = 0
        save_tasks()
        
        if task.task_type == TaskType.DATA_PROCESSING:
            result = await data_processing_task(task_id, task.parameters)
        elif task.task_type == TaskType.EMAIL_SIMULATION:
            result = await email_simulation_task(task_id, task.parameters)
        elif task.task_type == TaskType.IMAGE_PROCESSING:
            result = await image_processing_task(task_id, task.parameters)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
        
        task.status = TaskStatus.SUCCESS
        task.completed_at = datetime.now(timezone.utc).isoformat()
        task.result_data = result
        task.progress = 100
        
    except Exception as e:
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now(timezone.utc).isoformat()
        task.error_message = str(e)
    
    save_tasks()

async def task_worker():
    while True:
        try:
            task_id = await task_queue.get()
            
            if task_id in tasks_db:
                task = tasks_db[task_id]
                if task.status == TaskStatus.PENDING:
                    await execute_task(task_id)
            
            task_queue.task_done()
        except Exception as e:
            print(f"Worker error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global worker_task
    load_tasks()
    worker_task = asyncio.create_task(task_worker())
    
    for task_id, task in tasks_db.items():
        if task.status == TaskStatus.PENDING:
            await task_queue.put(task_id)
    
    yield
    
    if worker_task:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="Task Queue API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/tasks/submit", response_model=Task)
async def submit_task(request: TaskSubmitRequest):
    task_id = str(uuid.uuid4())
    
    task = Task(
        id=task_id,
        task_type=request.task_type,
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc).isoformat(),
        parameters=request.parameters
    )
    
    tasks_db[task_id] = task
    save_tasks()
    
    await task_queue.put(task_id)
    
    return task

@app.get("/api/tasks/", response_model=List[Task])
async def list_tasks(status: Optional[TaskStatus] = None, task_type: Optional[TaskType] = None):
    tasks = list(tasks_db.values())
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    if task_type:
        tasks = [t for t in tasks if t.task_type == task_type]
    
    tasks.sort(key=lambda t: t.created_at, reverse=True)
    
    return tasks

@app.get("/api/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks_db[task_id]

@app.delete("/api/tasks/{task_id}", response_model=Task)
async def cancel_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task.status == TaskStatus.RUNNING:
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc).isoformat()
        save_tasks()
    elif task.status == TaskStatus.PENDING:
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now(timezone.utc).isoformat()
        save_tasks()
    elif task.status in [TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel task with status {task.status}")
    
    return task

@app.post("/api/tasks/{task_id}/retry", response_model=Task)
async def retry_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks_db[task_id]
    
    if task.status != TaskStatus.FAILED:
        raise HTTPException(status_code=400, detail="Can only retry failed tasks")
    
    task.status = TaskStatus.PENDING
    task.started_at = None
    task.completed_at = None
    task.result_data = None
    task.error_message = None
    task.progress = 0
    
    save_tasks()
    
    await task_queue.put(task_id)
    
    return task

@app.get("/")
async def root():
    return {"message": "Task Queue API", "version": "1.0.0"}
