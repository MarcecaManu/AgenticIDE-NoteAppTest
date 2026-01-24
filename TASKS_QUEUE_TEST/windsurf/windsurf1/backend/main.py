from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import asyncio
import uuid
import json
import os
from pathlib import Path

app = FastAPI(title="Task Queue API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class TaskSubmit(BaseModel):
    task_type: TaskType
    parameters: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    id: str
    task_type: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    progress: Optional[int] = 0

class TaskQueue:
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.task_workers: Dict[str, asyncio.Task] = {}
        self.db_file = Path("backend/tasks.json")
        self.db_file.parent.mkdir(exist_ok=True)
        self.load_tasks()
    
    def load_tasks(self):
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                self.tasks = json.load(f)
    
    def save_tasks(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def create_task(self, task_type: TaskType, parameters: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "task_type": task_type.value,
            "status": TaskStatus.PENDING.value,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "completed_at": None,
            "result_data": None,
            "error_message": None,
            "progress": 0,
            "parameters": parameters
        }
        self.tasks[task_id] = task
        self.save_tasks()
        
        worker = asyncio.create_task(self.execute_task(task_id))
        self.task_workers[task_id] = worker
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict]:
        return list(self.tasks.values())
    
    def update_task(self, task_id: str, **kwargs):
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)
            self.save_tasks()
    
    def cancel_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task["status"] == TaskStatus.PENDING.value:
            self.update_task(
                task_id,
                status=TaskStatus.CANCELLED.value,
                completed_at=datetime.now(timezone.utc).isoformat()
            )
            
            if task_id in self.task_workers:
                self.task_workers[task_id].cancel()
                del self.task_workers[task_id]
            
            return True
        
        return False
    
    def retry_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        
        if task["status"] == TaskStatus.FAILED.value:
            self.update_task(
                task_id,
                status=TaskStatus.PENDING.value,
                started_at=None,
                completed_at=None,
                result_data=None,
                error_message=None,
                progress=0
            )
            
            worker = asyncio.create_task(self.execute_task(task_id))
            self.task_workers[task_id] = worker
            
            return True
        
        return False
    
    async def execute_task(self, task_id: str):
        task = self.tasks.get(task_id)
        if not task:
            return
        
        try:
            await asyncio.sleep(0.1)
            
            # Check if task still exists (might be cleared during tests)
            if task_id not in self.tasks:
                return
            
            if self.tasks[task_id]["status"] == TaskStatus.CANCELLED.value:
                return
            
            self.update_task(
                task_id,
                status=TaskStatus.RUNNING.value,
                started_at=datetime.now(timezone.utc).isoformat()
            )
            
            task_type = task["task_type"]
            parameters = task.get("parameters", {})
            
            if task_type == TaskType.DATA_PROCESSING.value:
                result = await self.process_data(task_id, parameters)
            elif task_type == TaskType.EMAIL_SIMULATION.value:
                result = await self.simulate_email(task_id, parameters)
            elif task_type == TaskType.IMAGE_PROCESSING.value:
                result = await self.process_image(task_id, parameters)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # Check if task still exists before updating
            if task_id in self.tasks:
                self.update_task(
                    task_id,
                    status=TaskStatus.SUCCESS.value,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    result_data=result,
                    progress=100
                )
            
        except asyncio.CancelledError:
            # Only update if task still exists
            if task_id in self.tasks:
                self.update_task(
                    task_id,
                    status=TaskStatus.CANCELLED.value,
                    completed_at=datetime.now(timezone.utc).isoformat()
                )
        except Exception as e:
            # Only update if task still exists
            if task_id in self.tasks:
                self.update_task(
                    task_id,
                    status=TaskStatus.FAILED.value,
                    completed_at=datetime.now(timezone.utc).isoformat(),
                    error_message=str(e)
                )
        finally:
            if task_id in self.task_workers:
                del self.task_workers[task_id]
    
    async def process_data(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        rows = parameters.get("rows", 1000)
        total_steps = 10
        
        processed_rows = 0
        results = {
            "total_rows": rows,
            "processed_rows": 0,
            "statistics": {
                "sum": 0,
                "average": 0,
                "min": 0,
                "max": 0
            }
        }
        
        values = []
        
        for step in range(total_steps):
            if self.tasks[task_id]["status"] == TaskStatus.CANCELLED.value:
                raise asyncio.CancelledError()
            
            await asyncio.sleep(1.5)
            
            rows_in_step = rows // total_steps
            for i in range(rows_in_step):
                value = (step * rows_in_step + i) % 100
                values.append(value)
                processed_rows += 1
            
            progress = int((step + 1) / total_steps * 100)
            self.update_task(task_id, progress=progress)
        
        results["processed_rows"] = processed_rows
        results["statistics"]["sum"] = sum(values)
        results["statistics"]["average"] = sum(values) / len(values) if values else 0
        results["statistics"]["min"] = min(values) if values else 0
        results["statistics"]["max"] = max(values) if values else 0
        
        return results
    
    async def simulate_email(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        recipients = parameters.get("recipients", ["user@example.com"])
        subject = parameters.get("subject", "Test Email")
        
        total_emails = len(recipients)
        sent_emails = []
        
        for i, recipient in enumerate(recipients):
            if self.tasks[task_id]["status"] == TaskStatus.CANCELLED.value:
                raise asyncio.CancelledError()
            
            await asyncio.sleep(2)
            
            sent_emails.append({
                "recipient": recipient,
                "subject": subject,
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "status": "sent"
            })
            
            progress = int((i + 1) / total_emails * 100)
            self.update_task(task_id, progress=progress)
        
        return {
            "total_emails": total_emails,
            "sent_emails": sent_emails,
            "success_count": len(sent_emails)
        }
    
    async def process_image(self, task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        images = parameters.get("images", ["image1.jpg", "image2.jpg", "image3.jpg"])
        operation = parameters.get("operation", "resize")
        
        total_images = len(images)
        processed_images = []
        
        for i, image in enumerate(images):
            if self.tasks[task_id]["status"] == TaskStatus.CANCELLED.value:
                raise asyncio.CancelledError()
            
            await asyncio.sleep(3)
            
            processed_images.append({
                "original": image,
                "operation": operation,
                "output": f"processed_{image}",
                "size": f"{800}x{600}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            })
            
            progress = int((i + 1) / total_images * 100)
            self.update_task(task_id, progress=progress)
        
        return {
            "total_images": total_images,
            "processed_images": processed_images,
            "operation": operation
        }

task_queue = TaskQueue()

@app.post("/api/tasks/submit", response_model=TaskResponse)
async def submit_task(task_submit: TaskSubmit):
    task_id = task_queue.create_task(task_submit.task_type, task_submit.parameters)
    task = task_queue.get_task(task_id)
    return TaskResponse(**task)

@app.get("/api/tasks/", response_model=List[TaskResponse])
async def list_tasks(status: Optional[str] = None, task_type: Optional[str] = None):
    tasks = task_queue.get_all_tasks()
    
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    
    if task_type:
        tasks = [t for t in tasks if t["task_type"] == task_type]
    
    tasks.sort(key=lambda x: x["created_at"], reverse=True)
    
    return [TaskResponse(**task) for task in tasks]

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = task_queue.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    success = task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"message": "Task cancelled successfully"}

@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str):
    success = task_queue.retry_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be retried")
    task = task_queue.get_task(task_id)
    return TaskResponse(**task)

@app.get("/")
async def root():
    return {"message": "Task Queue API is running"}
