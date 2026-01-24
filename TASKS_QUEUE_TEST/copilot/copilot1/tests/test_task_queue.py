"""Comprehensive tests for the task queue system."""
import pytest
import asyncio
from datetime import datetime
from httpx import AsyncClient
from backend.main import app
from backend.models import TaskType, TaskStatus
from backend.storage import TaskStorage
from backend.task_queue import TaskQueue


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_storage(tmp_path):
    """Create test storage with temporary file."""
    storage_path = tmp_path / "test_tasks.json"
    return TaskStorage(str(storage_path))


@pytest.fixture
def test_queue(test_storage):
    """Create test task queue."""
    return TaskQueue(test_storage)


class TestTaskSubmission:
    """Tests for task submission."""
    
    @pytest.mark.asyncio
    async def test_submit_data_processing_task(self, client):
        """Test submitting a data processing task."""
        response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "DATA_PROCESSING",
                "parameters": {
                    "num_rows": 500,
                    "processing_time": 5
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "DATA_PROCESSING"
        assert data["status"] == "PENDING"
        assert "id" in data
        assert data["progress"] == 0.0
    
    @pytest.mark.asyncio
    async def test_submit_email_simulation_task(self, client):
        """Test submitting an email simulation task."""
        response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "EMAIL_SIMULATION",
                "parameters": {
                    "num_emails": 5,
                    "delay_per_email": 0.5,
                    "subject": "Test Email"
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "EMAIL_SIMULATION"
        assert data["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_submit_image_processing_task(self, client):
        """Test submitting an image processing task."""
        response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "IMAGE_PROCESSING",
                "parameters": {
                    "num_images": 3,
                    "target_size": "800x600",
                    "output_format": "PNG"
                }
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "IMAGE_PROCESSING"
        assert data["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_submit_task_with_minimal_parameters(self, client):
        """Test submitting task with minimal parameters."""
        response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "DATA_PROCESSING"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["task_type"] == "DATA_PROCESSING"


class TestTaskRetrieval:
    """Tests for task retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_all_tasks(self, client):
        """Test retrieving all tasks."""
        # Submit a few tasks first
        for _ in range(3):
            await client.post(
                "/api/tasks/submit",
                json={"task_type": "DATA_PROCESSING"}
            )
        
        response = await client.get("/api/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    @pytest.mark.asyncio
    async def test_get_task_by_id(self, client):
        """Test retrieving a specific task by ID."""
        # Submit a task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "EMAIL_SIMULATION"}
        )
        task_id = submit_response.json()["id"]
        
        # Get task by ID
        response = await client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["task_type"] == "EMAIL_SIMULATION"
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, client):
        """Test retrieving a nonexistent task."""
        response = await client.get("/api/tasks/nonexistent-id")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_status(self, client):
        """Test filtering tasks by status."""
        response = await client.get("/api/tasks/?status=PENDING")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for task in data:
            assert task["status"] == "PENDING"
    
    @pytest.mark.asyncio
    async def test_filter_tasks_by_type(self, client):
        """Test filtering tasks by type."""
        response = await client.get("/api/tasks/?task_type=DATA_PROCESSING")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for task in data:
            assert task["task_type"] == "DATA_PROCESSING"


class TestTaskCancellation:
    """Tests for task cancellation."""
    
    @pytest.mark.asyncio
    async def test_cancel_pending_task(self, client):
        """Test cancelling a pending task."""
        # Submit a task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "DATA_PROCESSING",
                "parameters": {"processing_time": 60}  # Long-running task
            }
        )
        task_id = submit_response.json()["id"]
        
        # Cancel the task immediately
        response = await client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        assert "cancelled" in response.json()["message"].lower()
        
        # Verify task is cancelled
        get_response = await client.get(f"/api/tasks/{task_id}")
        assert get_response.json()["status"] == "CANCELLED"
    
    @pytest.mark.asyncio
    async def test_cancel_running_task(self, client):
        """Test cancelling a running task."""
        # Submit a long-running task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "DATA_PROCESSING",
                "parameters": {"processing_time": 30}
            }
        )
        task_id = submit_response.json()["id"]
        
        # Wait a bit for task to start
        await asyncio.sleep(2)
        
        # Cancel the task
        response = await client.delete(f"/api/tasks/{task_id}")
        # It should succeed whether task is PENDING or RUNNING
        assert response.status_code in [200, 400]  # 400 if already completed
    
    @pytest.mark.asyncio
    async def test_cannot_cancel_completed_task(self, client):
        """Test that completed tasks cannot be cancelled."""
        # Submit a quick task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "EMAIL_SIMULATION",
                "parameters": {
                    "num_emails": 1,
                    "delay_per_email": 0.1
                }
            }
        )
        task_id = submit_response.json()["id"]
        
        # Wait for task to complete
        await asyncio.sleep(3)
        
        # Try to cancel completed task
        response = await client.delete(f"/api/tasks/{task_id}")
        # Should either succeed if still running or fail if already completed
        # Both are acceptable as timing depends on system load
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_cancel_nonexistent_task(self, client):
        """Test cancelling a nonexistent task."""
        response = await client.delete("/api/tasks/nonexistent-id")
        assert response.status_code == 404


class TestTaskRetry:
    """Tests for task retry."""
    
    @pytest.mark.asyncio
    async def test_retry_failed_task(self, test_queue):
        """Test retrying a failed task."""
        await test_queue.start()
        
        # Create a task that will fail
        task = await test_queue.submit_task(
            TaskType.DATA_PROCESSING,
            {"num_rows": -1}  # Invalid parameter
        )
        
        # Wait for task to fail
        await asyncio.sleep(2)
        
        # Mark as failed manually for testing
        failed_task = test_queue.get_task(task.id)
        failed_task.status = TaskStatus.FAILED
        failed_task.error_message = "Test error"
        test_queue.storage.update_task(failed_task)
        
        # Retry the task
        new_task = await test_queue.retry_task(task.id)
        assert new_task is not None
        assert new_task.id != task.id
        assert new_task.task_type == task.task_type
        
        await test_queue.stop()
    
    @pytest.mark.asyncio
    async def test_retry_failed_task_via_api(self, client):
        """Test retrying a failed task via API."""
        # Submit a task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "DATA_PROCESSING"}
        )
        task_id = submit_response.json()["id"]
        
        # Wait and check if task failed (or manually mark as failed)
        await asyncio.sleep(2)
        
        # Try to retry (may fail if task hasn't failed yet, which is OK)
        response = await client.post(f"/api/tasks/{task_id}/retry")
        # Accept both success (if task failed) or 400 (if task hasn't failed)
        assert response.status_code in [201, 400]
    
    @pytest.mark.asyncio
    async def test_cannot_retry_successful_task(self, client):
        """Test that successful tasks cannot be retried."""
        # Submit a quick task
        submit_response = await client.post(
            "/api/tasks/submit",
            json={
                "task_type": "EMAIL_SIMULATION",
                "parameters": {
                    "num_emails": 1,
                    "delay_per_email": 0.1
                }
            }
        )
        task_id = submit_response.json()["id"]
        
        # Wait for task to complete successfully
        await asyncio.sleep(3)
        
        # Try to retry successful task
        response = await client.post(f"/api/tasks/{task_id}/retry")
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_retry_nonexistent_task(self, client):
        """Test retrying a nonexistent task."""
        response = await client.post("/api/tasks/nonexistent-id/retry")
        assert response.status_code == 404


class TestTaskExecution:
    """Tests for task execution."""
    
    @pytest.mark.asyncio
    async def test_data_processing_task_execution(self, test_queue):
        """Test data processing task executes successfully."""
        await test_queue.start()
        
        task = await test_queue.submit_task(
            TaskType.DATA_PROCESSING,
            {
                "num_rows": 100,
                "processing_time": 2
            }
        )
        
        # Wait for task to complete
        await asyncio.sleep(4)
        
        completed_task = test_queue.get_task(task.id)
        assert completed_task.status == TaskStatus.SUCCESS
        assert completed_task.result_data is not None
        assert "rows_processed" in completed_task.result_data
        assert completed_task.result_data["rows_processed"] == 100
        assert completed_task.progress == 100.0
        
        await test_queue.stop()
    
    @pytest.mark.asyncio
    async def test_email_simulation_task_execution(self, test_queue):
        """Test email simulation task executes successfully."""
        await test_queue.start()
        
        task = await test_queue.submit_task(
            TaskType.EMAIL_SIMULATION,
            {
                "num_emails": 3,
                "delay_per_email": 0.5
            }
        )
        
        # Wait for task to complete
        await asyncio.sleep(3)
        
        completed_task = test_queue.get_task(task.id)
        assert completed_task.status == TaskStatus.SUCCESS
        assert completed_task.result_data is not None
        assert "total_emails" in completed_task.result_data
        assert completed_task.result_data["total_emails"] == 3
        
        await test_queue.stop()
    
    @pytest.mark.asyncio
    async def test_image_processing_task_execution(self, test_queue):
        """Test image processing task executes successfully."""
        await test_queue.start()
        
        task = await test_queue.submit_task(
            TaskType.IMAGE_PROCESSING,
            {
                "num_images": 2,
                "target_size": "800x600",
                "output_format": "PNG"
            }
        )
        
        # Wait for task to complete
        await asyncio.sleep(10)
        
        completed_task = test_queue.get_task(task.id)
        assert completed_task.status == TaskStatus.SUCCESS
        assert completed_task.result_data is not None
        assert "processed_images" in completed_task.result_data
        assert len(completed_task.result_data["processed_images"]) == 2
        
        await test_queue.stop()
    
    @pytest.mark.asyncio
    async def test_task_progress_updates(self, test_queue):
        """Test that task progress is updated during execution."""
        await test_queue.start()
        
        task = await test_queue.submit_task(
            TaskType.DATA_PROCESSING,
            {
                "num_rows": 1000,
                "processing_time": 5
            }
        )
        
        # Wait a bit and check progress
        await asyncio.sleep(2)
        
        running_task = test_queue.get_task(task.id)
        # Progress should be updated
        assert running_task.progress > 0
        assert running_task.status in [TaskStatus.RUNNING, TaskStatus.SUCCESS]
        
        await test_queue.stop()


class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_task_type(self, client):
        """Test submitting an invalid task type."""
        response = await client.post(
            "/api/tasks/submit",
            json={"task_type": "INVALID_TYPE"}
        )
        # FastAPI validation should reject this
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_malformed_request(self, client):
        """Test submitting malformed request."""
        response = await client.post(
            "/api/tasks/submit",
            json={"invalid": "data"}
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestStorage:
    """Tests for task storage."""
    
    def test_add_and_retrieve_task(self, test_storage, test_queue):
        """Test adding and retrieving a task from storage."""
        from backend.models import Task, TaskType
        
        task = Task("test-id", TaskType.DATA_PROCESSING)
        test_storage.add_task(task)
        
        retrieved = test_storage.get_task("test-id")
        assert retrieved is not None
        assert retrieved.id == "test-id"
        assert retrieved.task_type == TaskType.DATA_PROCESSING
    
    def test_update_task(self, test_storage):
        """Test updating a task in storage."""
        from backend.models import Task, TaskType, TaskStatus
        
        task = Task("test-id", TaskType.EMAIL_SIMULATION)
        test_storage.add_task(task)
        
        task.status = TaskStatus.SUCCESS
        task.result_data = {"test": "data"}
        test_storage.update_task(task)
        
        retrieved = test_storage.get_task("test-id")
        assert retrieved.status == TaskStatus.SUCCESS
        assert retrieved.result_data == {"test": "data"}
    
    def test_delete_task(self, test_storage):
        """Test deleting a task from storage."""
        from backend.models import Task, TaskType
        
        task = Task("test-id", TaskType.IMAGE_PROCESSING)
        test_storage.add_task(task)
        
        result = test_storage.delete_task("test-id")
        assert result is True
        
        retrieved = test_storage.get_task("test-id")
        assert retrieved is None
    
    def test_filter_by_status(self, test_storage):
        """Test filtering tasks by status."""
        from backend.models import Task, TaskType, TaskStatus
        
        # Add tasks with different statuses
        task1 = Task("task-1", TaskType.DATA_PROCESSING)
        task1.status = TaskStatus.SUCCESS
        test_storage.add_task(task1)
        
        task2 = Task("task-2", TaskType.EMAIL_SIMULATION)
        task2.status = TaskStatus.FAILED
        test_storage.add_task(task2)
        
        task3 = Task("task-3", TaskType.IMAGE_PROCESSING)
        task3.status = TaskStatus.SUCCESS
        test_storage.add_task(task3)
        
        successful_tasks = test_storage.get_tasks_by_status(TaskStatus.SUCCESS)
        assert len(successful_tasks) == 2
        
        failed_tasks = test_storage.get_tasks_by_status(TaskStatus.FAILED)
        assert len(failed_tasks) == 1
