"""
API endpoint tests for task queue system
"""
import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.models import Base, Task
from backend.database import get_db_session
from backend.task_queue import task_queue

# Test database
TEST_DATABASE_URL = "sqlite:///./test_tasks.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override dependency
app.dependency_overrides[get_db_session] = override_get_db

# Configure task queue to use test database
task_queue.db_session_maker = TestSessionLocal

# Create test client
client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment once"""
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_tasks.db"):
        try:
            os.remove("./test_tasks.db")
        except Exception:
            pass


@pytest.fixture(scope="function", autouse=True)
def cleanup_database():
    """Clean up database between tests but don't recreate schema"""
    yield
    # Clear all tasks between tests
    db = TestSessionLocal()
    try:
        db.query(Task).delete()
        db.commit()
    finally:
        db.close()


class TestTaskSubmission:
    """Tests for task submission endpoint"""
    
    def test_submit_data_processing_task(self):
        """Test submitting a data processing task"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "data_processing",
                "parameters": {"rows": 100}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] in ["PENDING", "RUNNING"]
        assert data["task_type"] == "data_processing"
    
    def test_submit_email_simulation_task(self):
        """Test submitting an email simulation task"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "email_simulation",
                "parameters": {"count": 3}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] in ["PENDING", "RUNNING"]
        assert data["task_type"] == "email_simulation"
    
    def test_submit_image_processing_task(self):
        """Test submitting an image processing task"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "image_processing",
                "parameters": {"count": 2, "operation": "resize"}
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] in ["PENDING", "RUNNING"]
        assert data["task_type"] == "image_processing"
    
    def test_submit_invalid_task_type(self):
        """Test submitting task with invalid type"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "invalid_type",
                "parameters": {}
            }
        )
        
        assert response.status_code == 400
        assert "Invalid task type" in response.json()["detail"]


class TestTaskRetrieval:
    """Tests for task retrieval endpoints"""
    
    def test_list_all_tasks(self):
        """Test listing all tasks"""
        # Submit a task first
        client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        
        response = client.get("/api/tasks/")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) >= 1
        assert all("id" in task for task in tasks)
        assert all("status" in task for task in tasks)
    
    def test_filter_tasks_by_status(self):
        """Test filtering tasks by status"""
        # Submit a task
        client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        
        response = client.get("/api/tasks/?status=PENDING")
        assert response.status_code == 200
        tasks = response.json()
        assert all(task["status"] == "PENDING" for task in tasks)
    
    def test_filter_tasks_by_type(self):
        """Test filtering tasks by type"""
        # Submit a task
        client.post(
            "/api/tasks/submit",
            json={"task_type": "email_simulation", "parameters": {"count": 2}}
        )
        
        response = client.get("/api/tasks/?task_type=email_simulation")
        assert response.status_code == 200
        tasks = response.json()
        assert all(task["task_type"] == "email_simulation" for task in tasks)
    
    def test_get_specific_task(self):
        """Test getting specific task details"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        task_id = submit_response.json()["id"]
        
        # Get task details
        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        task = response.json()
        assert task["id"] == task_id
        assert task["task_type"] == "data_processing"
        assert "status" in task
    
    def test_get_nonexistent_task(self):
        """Test getting a non-existent task"""
        response = client.get("/api/tasks/nonexistent-id")
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]


class TestTaskCancellation:
    """Tests for task cancellation"""
    
    def test_cancel_pending_task(self):
        """Test cancelling a pending task"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        task_id = submit_response.json()["id"]
        
        # Cancel the task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"
        
        # Verify task is cancelled
        task_response = client.get(f"/api/tasks/{task_id}")
        assert task_response.json()["status"] == "CANCELLED"
    
    def test_cancel_nonexistent_task(self):
        """Test cancelling a non-existent task"""
        response = client.delete("/api/tasks/nonexistent-id")
        assert response.status_code == 404


class TestTaskRetry:
    """Tests for task retry functionality"""
    
    @pytest.mark.asyncio
    async def test_retry_failed_task(self):
        """Test retrying a failed task"""
        # This is a more complex test that would require simulating a failure
        # For now, we'll test the endpoint behavior
        submit_response = client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        task_id = submit_response.json()["id"]
        
        # Try to retry a non-failed task (should fail)
        response = client.post(f"/api/tasks/{task_id}/retry")
        # Should return 400 because task is not in FAILED status
        assert response.status_code == 400
        assert "cannot be retried" in response.json()["detail"]
    
    def test_retry_nonexistent_task(self):
        """Test retrying a non-existent task"""
        response = client.post("/api/tasks/nonexistent-id/retry")
        assert response.status_code == 404


class TestHealthCheck:
    """Tests for health check endpoint"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestTaskExecution:
    """Integration tests for task execution"""
    
    @pytest.mark.asyncio
    async def test_task_status_progression(self):
        """Test that task status progresses correctly"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json={"task_type": "data_processing", "parameters": {"rows": 100}}
        )
        task_id = submit_response.json()["id"]
        
        # Wait a bit and check status changes
        await asyncio.sleep(1)
        
        # Task should be PENDING or RUNNING
        response = client.get(f"/api/tasks/{task_id}")
        status = response.json()["status"]
        assert status in ["PENDING", "RUNNING", "SUCCESS"]
    
    @pytest.mark.asyncio
    async def test_multiple_tasks_concurrent(self):
        """Test submitting multiple tasks concurrently"""
        task_ids = []
        
        # Submit multiple tasks
        for i in range(3):
            response = client.post(
                "/api/tasks/submit",
                json={"task_type": "email_simulation", "parameters": {"count": 2}}
            )
            task_ids.append(response.json()["id"])
        
        assert len(task_ids) == 3
        
        # All tasks should be created
        for task_id in task_ids:
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            assert response.json()["id"] == task_id

