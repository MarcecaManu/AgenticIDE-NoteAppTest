"""Automated tests for Task Queue API."""
import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app, get_db_session
from models import Base, TaskStatus
from task_queue import task_queue


# Test database - use absolute path to avoid conflicts
test_db_path = os.path.join(os.path.dirname(__file__), 'test_tasks.db')
TEST_DATABASE_URL = f"sqlite:///{test_db_path}"
test_engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    echo=False
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Override dependency BEFORE creating test client
app.dependency_overrides[get_db_session] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Set up test database before each test."""
    # Delete existing test database if it exists
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except:
            pass
    
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    yield
    # Drop tables after test
    Base.metadata.drop_all(bind=test_engine)
    
    # Clean up test database file
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except:
            pass


@pytest.fixture(scope="function")
async def running_queue():
    """Start task queue for testing."""
    await task_queue.start_worker()
    yield task_queue
    await task_queue.stop_worker()


def test_health_check():
    """Test 1: Health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "queue_size" in data


def test_submit_data_processing_task():
    """Test 2: Submit data processing task."""
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "DATA_PROCESSING",
            "params": {"file_size": 100, "complexity": "low"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "DATA_PROCESSING"
    assert data["status"] == "PENDING"
    assert data["id"] is not None
    assert data["progress"] == 0.0


def test_submit_email_simulation_task():
    """Test 3: Submit email simulation task."""
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "EMAIL_SIMULATION",
            "params": {"recipient_count": 5, "template": "welcome"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "EMAIL_SIMULATION"
    assert data["status"] == "PENDING"


def test_submit_image_processing_task():
    """Test 4: Submit image processing task."""
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "IMAGE_PROCESSING",
            "params": {"image_count": 3, "operation": "resize"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task_type"] == "IMAGE_PROCESSING"
    assert data["status"] == "PENDING"


def test_submit_invalid_task_type():
    """Test 5: Submit invalid task type should fail."""
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "INVALID_TYPE",
            "params": {}
        }
    )
    assert response.status_code == 400


def test_list_tasks():
    """Test 6: List all tasks."""
    # Submit multiple tasks
    for i in range(3):
        client.post(
            "/api/tasks/submit",
            json={
                "task_type": "DATA_PROCESSING",
                "params": {"file_size": 100 + i}
            }
        )
    
    # List tasks
    response = client.get("/api/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(task["task_type"] == "DATA_PROCESSING" for task in data)


def test_filter_tasks_by_status():
    """Test 7: Filter tasks by status."""
    # Submit tasks
    task1 = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    ).json()
    
    task2 = client.post(
        "/api/tasks/submit",
        json={"task_type": "EMAIL_SIMULATION", "params": {}}
    ).json()
    
    # Filter by status
    response = client.get("/api/tasks/?status=PENDING")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["status"] == "PENDING" for task in data)


def test_filter_tasks_by_type():
    """Test 8: Filter tasks by type."""
    # Submit different task types
    client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    )
    client.post(
        "/api/tasks/submit",
        json={"task_type": "EMAIL_SIMULATION", "params": {}}
    )
    client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    )
    
    # Filter by type
    response = client.get("/api/tasks/?task_type=DATA_PROCESSING")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(task["task_type"] == "DATA_PROCESSING" for task in data)


def test_get_specific_task():
    """Test 9: Get specific task by ID."""
    # Submit task
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {"file_size": 500}}
    )
    task_id = submit_response.json()["id"]
    
    # Get task
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["task_type"] == "DATA_PROCESSING"


def test_get_nonexistent_task():
    """Test 10: Get nonexistent task should return 404."""
    response = client.get("/api/tasks/nonexistent-id")
    assert response.status_code == 404


def test_cancel_pending_task():
    """Test 11: Cancel a pending task."""
    # Submit task
    submit_response = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    )
    task_id = submit_response.json()["id"]
    
    # Cancel task
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["task_id"] == task_id
    
    # Verify task is cancelled
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.json()["status"] == "CANCELLED"


def test_cancel_nonexistent_task():
    """Test 12: Cancel nonexistent task should return 404."""
    response = client.delete("/api/tasks/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_task_execution_success():
    """Test 13: Task is queued and ready for execution."""
    # Note: This test verifies task queueing. Actual execution requires
    # the background worker which uses a separate database connection.
    # Integration tests would be needed to test end-to-end execution.
    
    # Submit task with quick execution
    response = client.post(
        "/api/tasks/submit",
        json={
            "task_type": "EMAIL_SIMULATION",
            "params": {"recipient_count": 2}
        }
    )
    assert response.status_code == 200
    task_id = response.json()["id"]
    
    # Verify task is in PENDING state (queued)
    get_response = client.get(f"/api/tasks/{task_id}")
    task = get_response.json()
    assert task["status"] == "PENDING"
    assert task["id"] == task_id
    
    # Verify task has correct input params
    input_params = json.loads(task["input_params"])
    assert input_params["recipient_count"] == 2


@pytest.mark.asyncio
async def test_retry_failed_task():
    """Test 14: Retry a failed task."""
    # This test would require simulating a failure
    # For now, we test the retry endpoint logic
    
    # Submit task
    response = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    )
    task_id = response.json()["id"]
    
    # Manually mark task as failed (for testing purposes)
    from models import Task
    db = TestSessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        task.status = TaskStatus.FAILED
        task.error_message = "Simulated failure"
        db.commit()
    finally:
        db.close()
    
    # Retry task
    retry_response = client.post(f"/api/tasks/{task_id}/retry")
    assert retry_response.status_code == 200
    new_task = retry_response.json()
    assert new_task["id"] != task_id
    assert new_task["status"] == "PENDING"
    assert new_task["retry_count"] == 1


def test_retry_non_failed_task():
    """Test 15: Retry non-failed task should fail."""
    # Submit task
    response = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": {}}
    )
    task_id = response.json()["id"]
    
    # Try to retry pending task
    retry_response = client.post(f"/api/tasks/{task_id}/retry")
    assert retry_response.status_code == 400


def test_task_input_params_stored():
    """Test 16: Task input parameters are stored correctly."""
    params = {"file_size": 1000, "complexity": "high"}
    response = client.post(
        "/api/tasks/submit",
        json={"task_type": "DATA_PROCESSING", "params": params}
    )
    task_id = response.json()["id"]
    
    # Get task
    get_response = client.get(f"/api/tasks/{task_id}")
    task = get_response.json()
    
    stored_params = json.loads(task["input_params"])
    assert stored_params == params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
