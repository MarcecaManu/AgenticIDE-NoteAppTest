import pytest
import time
from datetime import datetime
import json


class TestTaskSubmission:
    """Test task submission endpoint"""
    
    def test_submit_csv_processing_task(self, client, sample_task_data):
        """Test submitting a CSV processing task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["csv_processing"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "csv_processing"
        assert data["status"] == "PENDING"
        assert "id" in data
        assert data["created_at"] is not None
        assert data["progress"] == 0.0
    
    def test_submit_email_sending_task(self, client, sample_task_data):
        """Test submitting an email sending task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["email_sending"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "email_sending"
        assert data["status"] == "PENDING"
        assert "id" in data
    
    def test_submit_image_processing_task(self, client, sample_task_data):
        """Test submitting an image processing task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["image_processing"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "image_processing"
        assert data["status"] == "PENDING"
        assert "id" in data
    
    def test_submit_invalid_task_type(self, client):
        """Test submitting a task with invalid task type"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "invalid_task",
                "input_params": {}
            }
        )
        
        assert response.status_code == 400
        assert "Invalid task type" in response.json()["detail"]


class TestTaskRetrieval:
    """Test task retrieval endpoints"""
    
    def test_list_empty_tasks(self, client):
        """Test listing tasks when none exist"""
        response = client.get("/api/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["tasks"] == []
        assert data["total"] == 0
    
    def test_list_tasks(self, client, sample_task_data):
        """Test listing tasks after submission"""
        # Submit multiple tasks
        for task_type in ["csv_processing", "email_sending", "image_processing"]:
            client.post("/api/tasks/submit", json=sample_task_data[task_type])
        
        response = client.get("/api/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["tasks"]) == 3
    
    def test_filter_tasks_by_status(self, client, sample_task_data):
        """Test filtering tasks by status"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["csv_processing"]
        )
        
        # Filter by PENDING status
        response = client.get("/api/tasks/?status=PENDING")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(task["status"] == "PENDING" for task in data["tasks"])
    
    def test_filter_tasks_by_type(self, client, sample_task_data):
        """Test filtering tasks by type"""
        # Submit tasks of different types
        client.post("/api/tasks/submit", json=sample_task_data["csv_processing"])
        client.post("/api/tasks/submit", json=sample_task_data["email_sending"])
        
        # Filter by csv_processing type
        response = client.get("/api/tasks/?task_type=csv_processing")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(task["task_type"] == "csv_processing" for task in data["tasks"])
    
    def test_get_specific_task(self, client, sample_task_data):
        """Test retrieving a specific task by ID"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["csv_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Get the task
        response = client.get(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["task_type"] == "csv_processing"
    
    def test_get_nonexistent_task(self, client):
        """Test retrieving a task that doesn't exist"""
        response = client.get("/api/tasks/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestTaskCancellation:
    """Test task cancellation"""
    
    def test_cancel_pending_task(self, client, sample_task_data):
        """Test cancelling a pending task"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["csv_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Cancel the task
        response = client.delete(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        assert response.json()["task_id"] == task_id
        
        # Verify task is cancelled
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.json()["status"] == "CANCELLED"
    
    def test_cancel_nonexistent_task(self, client):
        """Test cancelling a task that doesn't exist"""
        response = client.delete("/api/tasks/nonexistent-id")
        
        assert response.status_code == 404
    
    def test_cannot_cancel_completed_task(self, client, sample_task_data, db_session):
        """Test that completed tasks cannot be cancelled"""
        from database import TaskModel
        
        # Create a completed task directly in database
        task = TaskModel(
            id="test-completed-task",
            task_type="csv_processing",
            status="SUCCESS",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        db_session.add(task)
        db_session.commit()
        
        # Try to cancel it
        response = client.delete("/api/tasks/test-completed-task")
        
        assert response.status_code == 400
        assert "Cannot cancel" in response.json()["detail"]


class TestTaskRetry:
    """Test task retry functionality"""
    
    def test_retry_failed_task(self, client, sample_task_data, db_session):
        """Test retrying a failed task"""
        from database import TaskModel
        
        # Create a failed task directly in database
        failed_task = TaskModel(
            id="test-failed-task",
            task_type="csv_processing",
            status="FAILED",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            error_message="Test error",
            input_params=json.dumps(sample_task_data["csv_processing"]["input_params"])
        )
        db_session.add(failed_task)
        db_session.commit()
        
        # Retry the task
        response = client.post("/api/tasks/test-failed-task/retry")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["task_type"] == "csv_processing"
        assert data["id"] != "test-failed-task"  # Should have new ID
    
    def test_retry_cancelled_task(self, client, sample_task_data, db_session):
        """Test retrying a cancelled task"""
        from database import TaskModel
        
        # Create a cancelled task
        cancelled_task = TaskModel(
            id="test-cancelled-task",
            task_type="email_sending",
            status="CANCELLED",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            input_params=json.dumps(sample_task_data["email_sending"]["input_params"])
        )
        db_session.add(cancelled_task)
        db_session.commit()
        
        # Retry the task
        response = client.post("/api/tasks/test-cancelled-task/retry")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PENDING"
        assert data["task_type"] == "email_sending"
    
    def test_cannot_retry_success_task(self, client, db_session):
        """Test that successful tasks cannot be retried"""
        from database import TaskModel
        
        # Create a successful task
        success_task = TaskModel(
            id="test-success-task",
            task_type="csv_processing",
            status="SUCCESS",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            input_params="{}"
        )
        db_session.add(success_task)
        db_session.commit()
        
        # Try to retry it
        response = client.post("/api/tasks/test-success-task/retry")
        
        assert response.status_code == 400
        assert "Cannot retry" in response.json()["detail"]
    
    def test_retry_nonexistent_task(self, client):
        """Test retrying a task that doesn't exist"""
        response = client.post("/api/tasks/nonexistent-id/retry")
        
        assert response.status_code == 404


class TestTaskStatusMonitoring:
    """Test task status monitoring and updates"""
    
    def test_task_status_transitions(self, client, sample_task_data, db_session):
        """Test that task status transitions correctly"""
        from database import TaskModel
        
        # Create tasks in different states
        tasks = [
            TaskModel(id="pending-task", task_type="csv_processing", status="PENDING", created_at=datetime.utcnow()),
            TaskModel(id="running-task", task_type="csv_processing", status="RUNNING", created_at=datetime.utcnow(), started_at=datetime.utcnow()),
            TaskModel(id="success-task", task_type="csv_processing", status="SUCCESS", created_at=datetime.utcnow(), completed_at=datetime.utcnow()),
            TaskModel(id="failed-task", task_type="csv_processing", status="FAILED", created_at=datetime.utcnow(), completed_at=datetime.utcnow()),
        ]
        
        for task in tasks:
            db_session.add(task)
        db_session.commit()
        
        # Verify each status
        for task_id in ["pending-task", "running-task", "success-task", "failed-task"]:
            response = client.get(f"/api/tasks/{task_id}")
            assert response.status_code == 200
            data = response.json()
            expected_status = task_id.split("-")[0].upper()
            assert data["status"] == expected_status
    
    def test_progress_tracking(self, client, db_session):
        """Test that progress is tracked correctly"""
        from database import TaskModel
        
        # Create a task with progress
        task = TaskModel(
            id="progress-task",
            task_type="csv_processing",
            status="RUNNING",
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            progress=45.5
        )
        db_session.add(task)
        db_session.commit()
        
        # Get task and verify progress
        response = client.get("/api/tasks/progress-task")
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 45.5


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns healthy status"""
        response = client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

