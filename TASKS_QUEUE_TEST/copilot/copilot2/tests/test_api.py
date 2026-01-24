"""
Comprehensive tests for the Task Queue & Background Processing system.
Tests cover task submission, status monitoring, cancellation, retry logic,
different task types, and error handling.
"""

import pytest
import time
from unittest.mock import patch, MagicMock


class TestTaskSubmission:
    """Test task submission functionality"""
    
    def test_submit_data_processing_task(self, client, sample_task_data):
        """Test 1: Submit a data processing task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["task_type"] == "data_processing"
        assert data["status"] == "PENDING"
        assert data["progress"] == 0
    
    def test_submit_email_simulation_task(self, client, sample_task_data):
        """Test 2: Submit an email simulation task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["email_simulation"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "email_simulation"
        assert data["status"] == "PENDING"
    
    def test_submit_image_processing_task(self, client, sample_task_data):
        """Test 3: Submit an image processing task"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["image_processing"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "image_processing"
        assert data["status"] == "PENDING"
    
    def test_submit_invalid_task_type(self, client):
        """Test 4: Submit task with invalid task type"""
        response = client.post(
            "/api/tasks/submit",
            json={
                "task_type": "invalid_type",
                "input_data": {}
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_uppercase_task_type(self, client, sample_task_data):
        """Test: Submit task with uppercase task type"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing_alt"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "data_processing"
        assert data["status"] == "PENDING"
    
    def test_submit_with_parameters_field(self, client, sample_task_data):
        """Test: Submit task using 'parameters' instead of 'input_data'"""
        response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["email_simulation_alt"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["task_type"] == "email_simulation"
        assert data["status"] == "PENDING"


class TestTaskStatusMonitoring:
    """Test task status monitoring functionality"""
    
    def test_list_all_tasks(self, client, sample_task_data):
        """Test 5: List all tasks"""
        # Submit multiple tasks (only the original 3 types)
        original_types = ["data_processing", "email_simulation", "image_processing"]
        for task_type in original_types:
            client.post("/api/tasks/submit", json=sample_task_data[task_type])
        
        # List all tasks
        response = client.get("/api/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["tasks"]) == 3
    
    def test_filter_tasks_by_status(self, client, sample_task_data):
        """Test 6: Filter tasks by status"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Filter by PENDING status
        response = client.get("/api/tasks/?status=PENDING")
        
        assert response.status_code == 200
        data = response.json()
        assert all(task["status"] == "PENDING" for task in data["tasks"])
        assert any(task["id"] == task_id for task in data["tasks"])
    
    def test_filter_tasks_by_type(self, client, sample_task_data):
        """Test 7: Filter tasks by type"""
        # Submit tasks of different types
        client.post("/api/tasks/submit", json=sample_task_data["data_processing"])
        client.post("/api/tasks/submit", json=sample_task_data["email_simulation"])
        
        # Filter by data_processing type
        response = client.get("/api/tasks/?task_type=data_processing")
        
        assert response.status_code == 200
        data = response.json()
        assert all(task["task_type"] == "data_processing" for task in data["tasks"])
    
    def test_get_specific_task(self, client, sample_task_data):
        """Test 8: Get specific task by ID"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Get specific task
        response = client.get(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["task_type"] == "data_processing"
    
    def test_get_nonexistent_task(self, client):
        """Test 9: Get nonexistent task returns 404"""
        response = client.get("/api/tasks/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestTaskCancellation:
    """Test task cancellation functionality"""
    
    def test_cancel_pending_task(self, client, sample_task_data):
        """Test 10: Cancel a pending task"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Cancel the task
        response = client.delete(f"/api/tasks/{task_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELLED"
        
        # Verify task is cancelled
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.json()["status"] == "CANCELLED"
    
    def test_cancel_nonexistent_task(self, client):
        """Test 11: Cancel nonexistent task returns 404"""
        response = client.delete("/api/tasks/nonexistent-id")
        
        assert response.status_code == 404


class TestTaskRetry:
    """Test task retry functionality"""
    
    @patch('backend.main.data_processing_task')
    def test_retry_failed_task(self, mock_task, client, sample_task_data, test_db):
        """Test 12: Retry a failed task"""
        # Mock the Celery task
        mock_task.apply_async = MagicMock()
        
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Manually set task to FAILED status
        from backend.database import TaskDB
        task = test_db.query(TaskDB).filter(TaskDB.id == task_id).first()
        task.status = "FAILED"
        task.error_message = "Simulated failure"
        test_db.commit()
        
        # Retry the task
        response = client.post(f"/api/tasks/{task_id}/retry")
        
        assert response.status_code == 200
        data = response.json()
        assert "new_task_id" in data
        assert data["new_task_id"] != task_id
        
        # Verify new task was created
        new_task_response = client.get(f"/api/tasks/{data['new_task_id']}")
        assert new_task_response.status_code == 200
        assert new_task_response.json()["status"] == "PENDING"
    
    def test_retry_non_failed_task(self, client, sample_task_data):
        """Test 13: Cannot retry non-failed task"""
        # Submit a task
        submit_response = client.post(
            "/api/tasks/submit",
            json=sample_task_data["data_processing"]
        )
        task_id = submit_response.json()["id"]
        
        # Try to retry a pending task (should fail)
        response = client.post(f"/api/tasks/{task_id}/retry")
        
        assert response.status_code == 400
        assert "only retry failed tasks" in response.json()["detail"].lower()


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_malformed_request_body(self, client):
        """Test 14: Handle malformed request body"""
        response = client.post(
            "/api/tasks/submit",
            json={"invalid": "data"}
        )
        
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test 15: Handle missing required fields"""
        response = client.post(
            "/api/tasks/submit",
            json={}
        )
        
        assert response.status_code == 422
    
    def test_pagination_limits(self, client, sample_task_data):
        """Test 16: Test pagination with limits"""
        # Submit multiple tasks
        for _ in range(5):
            client.post("/api/tasks/submit", json=sample_task_data["data_processing"])
        
        # Request with limit
        response = client.get("/api/tasks/?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 3
        assert data["total"] == 5
    
    def test_pagination_offset(self, client, sample_task_data):
        """Test 17: Test pagination with offset"""
        # Submit multiple tasks
        for _ in range(5):
            client.post("/api/tasks/submit", json=sample_task_data["data_processing"])
        
        # Request with offset
        response = client.get("/api/tasks/?offset=2&limit=2")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) <= 2


class TestHealthCheck:
    """Test system health check"""
    
    def test_health_endpoint(self, client):
        """Test 18: Health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_root_endpoint(self, client):
        """Test 19: Root endpoint returns API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert "version" in data
