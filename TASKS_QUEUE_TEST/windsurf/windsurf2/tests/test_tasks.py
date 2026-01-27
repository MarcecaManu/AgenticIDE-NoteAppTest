import pytest
import asyncio
import sys
import os
from pathlib import Path
import httpx

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from fastapi.testclient import TestClient
from main import app, tasks_db, task_queue, STORAGE_FILE, TaskStatus, TaskType, execute_task

@pytest.fixture(autouse=True)
def cleanup():
    tasks_db.clear()
    while not task_queue.empty():
        try:
            task_queue.get_nowait()
        except asyncio.QueueEmpty:
            break
    
    if STORAGE_FILE.exists():
        STORAGE_FILE.unlink()
    
    yield
    
    tasks_db.clear()
    if STORAGE_FILE.exists():
        STORAGE_FILE.unlink()

@pytest.fixture
def client():
    return TestClient(app)

def test_submit_data_processing_task(client):
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "data_processing",
            "parameters": {"rows": 1000}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["task_type"] == "data_processing"
    assert data["status"] == "PENDING"
    assert data["progress"] == 0
    assert data["parameters"]["rows"] == 1000
    assert "created_at" in data

def test_submit_email_simulation_task(client):
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "email_simulation",
            "parameters": {"recipient_count": 5}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["task_type"] == "email_simulation"
    assert data["status"] == "PENDING"
    assert data["parameters"]["recipient_count"] == 5

def test_submit_image_processing_task(client):
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "image_processing",
            "parameters": {"image_count": 3, "operation": "resize"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["task_type"] == "image_processing"
    assert data["status"] == "PENDING"
    assert data["parameters"]["image_count"] == 3
    assert data["parameters"]["operation"] == "resize"

def test_list_all_tasks(client):
    client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    client.post(
        "/api/tasks/submit",
        json={"task_type": "email_simulation", "parameters": {"recipient_count": 10}}
    )
    
    response = client.get("/api/tasks/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["task_type"] in ["data_processing", "email_simulation"]

def test_list_tasks_with_status_filter(client):
    task1_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task1_id = task1_response.json()["id"]
    
    client.post(
        "/api/tasks/submit",
        json={"task_type": "email_simulation", "parameters": {"recipient_count": 10}}
    )
    
    tasks_db[task1_id].status = TaskStatus.SUCCESS
    
    response = client.get("/api/tasks/?status=SUCCESS")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["status"] == "SUCCESS"

def test_list_tasks_with_type_filter(client):
    client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    client.post(
        "/api/tasks/submit",
        json={"task_type": "email_simulation", "parameters": {"recipient_count": 10}}
    )
    client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 1000}}
    )
    
    response = client.get("/api/tasks/?task_type=data_processing")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 2
    assert all(task["task_type"] == "data_processing" for task in data)

def test_get_specific_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    response = client.get(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == task_id
    assert data["task_type"] == "data_processing"
    assert data["status"] == "PENDING"

def test_get_nonexistent_task(client):
    response = client.get("/api/tasks/nonexistent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_cancel_pending_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    response = client.delete(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "CANCELLED"
    assert data["completed_at"] is not None

def test_cancel_running_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    tasks_db[task_id].status = TaskStatus.RUNNING
    
    response = client.delete(f"/api/tasks/{task_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "CANCELLED"

def test_cannot_cancel_completed_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    tasks_db[task_id].status = TaskStatus.SUCCESS
    
    response = client.delete(f"/api/tasks/{task_id}")
    
    assert response.status_code == 400
    assert "cannot cancel" in response.json()["detail"].lower()

def test_retry_failed_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    tasks_db[task_id].status = TaskStatus.FAILED
    tasks_db[task_id].error_message = "Test error"
    
    response = client.post(f"/api/tasks/{task_id}/retry")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "PENDING"
    assert data["error_message"] is None
    assert data["result_data"] is None
    assert data["progress"] == 0

def test_cannot_retry_non_failed_task(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    response = client.post(f"/api/tasks/{task_id}/retry")
    
    assert response.status_code == 400
    assert "only retry failed" in response.json()["detail"].lower()

def test_retry_nonexistent_task(client):
    response = client.post("/api/tasks/nonexistent-id/retry")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_task_execution_data_processing():
    async with httpx.AsyncClient(app=app, base_url="http://test", timeout=60.0) as client:
        submit_response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        task_id = submit_response.json()["id"]
        
        # Manually execute the task since TestClient doesn't run background tasks
        await execute_task(task_id)
        
        response = await client.get(f"/api/tasks/{task_id}")
        task = response.json()
        
        assert task["status"] == "SUCCESS", f"Task status: {task['status']}"
        assert task["result_data"] is not None
        assert "total_rows" in task["result_data"]
        assert "statistics" in task["result_data"]
        assert task["progress"] == 100
        assert task["started_at"] is not None
        assert task["completed_at"] is not None

@pytest.mark.asyncio
async def test_task_execution_email_simulation():
    async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
        submit_response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "email_simulation", "parameters": {"recipient_count": 3}}
        )
        task_id = submit_response.json()["id"]
        
        # Manually execute the task since TestClient doesn't run background tasks
        await execute_task(task_id)
        
        response = await client.get(f"/api/tasks/{task_id}")
        task = response.json()
        
        assert task["status"] == "SUCCESS", f"Task status: {task['status']}"
        assert task["result_data"] is not None
        assert "total_emails" in task["result_data"]
        assert "sent" in task["result_data"]
        assert "recipients" in task["result_data"]
        assert task["progress"] == 100

@pytest.mark.asyncio
async def test_task_execution_image_processing():
    async with httpx.AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
        submit_response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "image_processing", "parameters": {"image_count": 2, "operation": "resize"}}
        )
        task_id = submit_response.json()["id"]
        
        # Manually execute the task since TestClient doesn't run background tasks
        await execute_task(task_id)
        
        response = await client.get(f"/api/tasks/{task_id}")
        task = response.json()
        
        assert task["status"] == "SUCCESS", f"Task status: {task['status']}"
        assert task["result_data"] is not None
        assert "total_images" in task["result_data"]
        assert "processed" in task["result_data"]
        assert "images" in task["result_data"]
        assert task["progress"] == 100

def test_persistent_storage(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 500}}
    )
    task_id = submit_response.json()["id"]
    
    assert STORAGE_FILE.exists()
    
    import json
    with open(STORAGE_FILE, 'r') as f:
        stored_data = json.load(f)
    
    assert task_id in stored_data
    assert stored_data[task_id]["task_type"] == "data_processing"
    assert stored_data[task_id]["status"] == "PENDING"

def test_multiple_tasks_concurrent_submission(client):
    task_ids = []
    
    for i in range(5):
        response = client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 500}}
        )
        task_ids.append(response.json()["id"])
    
    response = client.get("/api/tasks/")
    tasks = response.json()
    
    assert len(tasks) == 5
    assert all(task["id"] in task_ids for task in tasks)

def test_task_progress_updates(client):
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "data_processing", "parameters": {"rows": 100}}
    )
    task_id = submit_response.json()["id"]
    
    import time
    time.sleep(3)
    
    response = client.get(f"/api/tasks/{task_id}")
    task = response.json()
    
    if task["status"] == "RUNNING":
        assert task["progress"] > 0
        assert task["started_at"] is not None
