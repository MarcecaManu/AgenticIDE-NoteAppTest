from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from models import TaskSubmit, TaskResponse, TaskStatus, TaskType
from storage import TaskStorage
from task_queue import TaskQueue
from contextlib import asynccontextmanager

task_storage = TaskStorage()
task_queue = TaskQueue(task_storage)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await task_queue.start_worker()
    yield
    await task_queue.stop_worker()

app = FastAPI(title="Task Queue API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def task_to_response(task) -> TaskResponse:
    try:
        # Safely convert datetime objects to ISO format strings
        created_at_str = task.created_at.isoformat() if task.created_at else None
        started_at_str = task.started_at.isoformat() if task.started_at else None
        completed_at_str = task.completed_at.isoformat() if task.completed_at else None
        
        return TaskResponse(
            id=task.id,
            task_type=task.task_type,
            status=task.status,
            created_at=created_at_str,
            started_at=started_at_str,
            completed_at=completed_at_str,
            result_data=task.result_data,
            error_message=task.error_message,
            progress=task.progress
        )
    except Exception as e:
        # If there's any error, log it and re-raise
        print(f"Error converting task to response: {e}, task: {task}")
        raise

@app.post("/api/tasks/submit", response_model=TaskResponse)
async def submit_task(task_submit: TaskSubmit):
    try:
        task = await task_queue.submit_task(task_submit.task_type, task_submit.parameters)
        return task_to_response(task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/", response_model=List[TaskResponse])
async def list_tasks(status: Optional[TaskStatus] = None, task_type: Optional[TaskType] = None):
    try:
        tasks = await task_storage.get_all_tasks()
        
        if status:
            tasks = [t for t in tasks if t.status == status]
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        
        tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        # Convert tasks to responses one by one with error handling
        responses = []
        for task in tasks:
            try:
                responses.append(task_to_response(task))
            except Exception as task_error:
                print(f"Error converting task {task.id}: {task_error}")
                print(f"Task details: id={task.id}, type={task.task_type}, status={task.status}")
                print(f"Task created_at type: {type(task.created_at)}, value: {task.created_at}")
                raise
        
        return responses
    except Exception as e:
        import traceback
        print(f"Error in list_tasks: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    task = await task_storage.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_to_response(task)

@app.delete("/api/tasks/{task_id}")
async def cancel_task(task_id: str):
    success = await task_queue.cancel_task(task_id)
    if not success:
        raise HTTPException(status_code=400, detail="Task cannot be cancelled")
    return {"message": "Task cancelled successfully"}

@app.post("/api/tasks/{task_id}/retry", response_model=TaskResponse)
async def retry_task(task_id: str):
    new_task = await task_queue.retry_task(task_id)
    if not new_task:
        raise HTTPException(status_code=400, detail="Task cannot be retried")
    return task_to_response(new_task)

@app.get("/")
async def root():
    return {"message": "Task Queue API is running"}
