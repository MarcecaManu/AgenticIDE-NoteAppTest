import pytest
import sys
import os
from pathlib import Path

backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
import time

# Create app without lifespan for testing
def get_test_app():
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from typing import List, Optional
    from models import TaskSubmit, TaskResponse, TaskStatus, TaskType
    from storage import TaskStorage
    from task_queue import TaskQueue
    
    app = FastAPI(title="Task Queue API")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    task_storage = TaskStorage("test_tasks.json")
    task_queue = TaskQueue(task_storage)
    
    def task_to_response(task) -> TaskResponse:
        return TaskResponse(
            id=task.id,
            task_type=task.task_type,
            status=task.status,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            result_data=task.result_data,
            error_message=task.error_message,
            progress=task.progress
        )
    
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
            
            return [task_to_response(task) for task in tasks]
        except Exception as e:
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
    
    # Store references for cleanup
    app.state.task_storage = task_storage
    app.state.task_queue = task_queue
    
    return app

@pytest.fixture
def client():
    test_storage_file = "test_tasks.json"
    if os.path.exists(test_storage_file):
        os.remove(test_storage_file)
    
    app = get_test_app()
    client = TestClient(app)
    
    yield client
    
    if os.path.exists(test_storage_file):
        os.remove(test_storage_file)

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Queue API is running"}

def test_submit_data_processing_task(client):
    response = client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {
            "rows": 500,
            "processing_time": 1
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "data_processing"
    assert data["status"] == "PENDING"
    assert "id" in data

def test_submit_email_simulation_task(client):
    response = client.post("/api/tasks/submit", json={
        "task_type": "email_simulation",
        "parameters": {
            "recipient_count": 3,
            "delay_per_email": 0.2,
            "subject": "Test Email"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "email_simulation"
    assert data["status"] == "PENDING"

def test_submit_image_processing_task(client):
    response = client.post("/api/tasks/submit", json={
        "task_type": "image_processing",
        "parameters": {
            "image_count": 2,
            "operation": "resize",
            "processing_time": 1
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "image_processing"
    assert data["status"] == "PENDING"

def test_list_all_tasks(client):
    client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    
    client.post("/api/tasks/submit", json={
        "task_type": "email_simulation",
        "parameters": {"recipient_count": 2, "delay_per_email": 0.2}
    })
    
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_specific_task(client):
    submit_response = client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    task_id = submit_response.json()["id"]
    
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id

def test_get_nonexistent_task(client):
    response = client.get("/api/tasks/nonexistent-id")
    assert response.status_code == 404

def test_cancel_pending_task(client):
    submit_response = client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 10}
    })
    task_id = submit_response.json()["id"]
    
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.json()["status"] == "CANCELLED"

def test_retry_failed_task(client):
    submit_response = client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    task_id = submit_response.json()["id"]
    
    # Mark as failed using the app's storage
    from models import TaskStatus
    from datetime import datetime, timezone
    import asyncio
    
    async def mark_failed():
        # Access the storage from the app state
        storage = client.app.state.task_storage
        await storage.update_task_status(
            task_id,
            TaskStatus.FAILED,
            completed_at=datetime.now(timezone.utc),
            error_message="Test error"
        )
    
    asyncio.run(mark_failed())
    
    retry_response = client.post(f"/api/tasks/{task_id}/retry")
    assert retry_response.status_code == 200
    new_task = retry_response.json()
    assert new_task["id"] != task_id
    assert new_task["status"] == "PENDING"

def test_filter_tasks_by_status(client):
    client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    
    response = client.get("/api/tasks/?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert all(task["status"] == "PENDING" for task in data)

def test_filter_tasks_by_type(client):
    client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    
    client.post("/api/tasks/submit", json={
        "task_type": "email_simulation",
        "parameters": {"recipient_count": 2, "delay_per_email": 0.2}
    })
    
    response = client.get("/api/tasks/?task_type=data_processing")
    assert response.status_code == 200
    data = response.json()
    assert all(task["task_type"] == "data_processing" for task in data)

def test_cancel_nonexistent_task(client):
    response = client.delete("/api/tasks/nonexistent-id")
    assert response.status_code == 400

def test_retry_non_failed_task(client):
    submit_response = client.post("/api/tasks/submit", json={
        "task_type": "data_processing",
        "parameters": {"rows": 100, "processing_time": 1}
    })
    task_id = submit_response.json()["id"]
    
    retry_response = client.post(f"/api/tasks/{task_id}/retry")
    assert retry_response.status_code == 400
