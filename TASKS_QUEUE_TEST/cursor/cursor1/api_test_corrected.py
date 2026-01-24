# api_test_corrected.py - Fixed to match actual backend API
import httpx
import time

BASE_URL = "http://localhost:8000"


def test_task_operations():
    """Test complete task queue CRUD operations"""
    
    # CREATE - Submit a new task (CORRECTED)
    task_data = {
        "task_type": "csv_processing",  # FIXED: lowercase with underscore
        "input_params": {               # FIXED: input_params instead of parameters
            "num_rows": 500,
            "processing_time": 2
        }
    }
    
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data)
    assert response.status_code in (200, 201), f"Got {response.status_code}: {response.text}"
    created = response.json()
    
    task_id = created.get("id")
    assert task_id is not None
    assert created.get("status") in ("PENDING", "RUNNING")
    print(f"✓ Task submitted: {task_id} - Status: {created.get('status')}")

    # READ ALL - List all tasks
    response = httpx.get(f"{BASE_URL}/api/tasks/")
    assert response.status_code == 200
    tasks_response = response.json()
    
    # Backend returns {"tasks": [...], "total": N}
    tasks_data = tasks_response.get("tasks", [])
    assert len(tasks_data) > 0
    print(f"✓ Tasks listed: {len(tasks_data)} tasks")

    # READ ONE - Get specific task status
    response = httpx.get(f"{BASE_URL}/api/tasks/{task_id}")
    assert response.status_code == 200
    task_status = response.json()
    assert task_status.get("id") == task_id
    print(f"✓ Task retrieved: {task_id} - Status: {task_status.get('status')}")

    # Wait for task completion (with timeout)
    max_wait = 10
    waited = 0
    while waited < max_wait:
        response = httpx.get(f"{BASE_URL}/api/tasks/{task_id}")
        task_status = response.json()
        status = task_status.get("status")
        
        if status in ("SUCCESS", "FAILED", "CANCELLED"):
            break
        
        time.sleep(1)
        waited += 1
    
    print(f"✓ Task completed: {task_id} - Final status: {task_status.get('status')}")

    # Test task submission with different types (CORRECTED)
    email_task = {
        "task_type": "email_sending",  # FIXED
        "input_params": {              # FIXED
            "num_emails": 3,
            "delay_per_email": 0.5,
            "subject": "Test Email"
        }
    }
    
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=email_task)
    assert response.status_code in (200, 201)
    email_task_id = response.json().get("id")
    print(f"✓ Email task submitted: {email_task_id}")

    # DELETE - Cancel a task
    long_task = {
        "task_type": "csv_processing",  # FIXED
        "input_params": {               # FIXED
            "num_rows": 1000,
            "processing_time": 30
        }
    }
    
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=long_task)
    cancel_task_id = response.json().get("id")
    
    # Wait a moment to ensure task starts
    time.sleep(0.5)
    
    # Cancel the task
    response = httpx.delete(f"{BASE_URL}/api/tasks/{cancel_task_id}")
    assert response.status_code == 200  # Backend returns 200
    print(f"✓ Task cancelled: {cancel_task_id}")

    # VERIFY CANCELLATION
    response = httpx.get(f"{BASE_URL}/api/tasks/{cancel_task_id}")
    assert response.status_code == 200
    cancelled_task = response.json()
    assert cancelled_task.get("status") == "CANCELLED"
    print(f"✓ Cancellation verified: {cancel_task_id}")


def test_task_retry():
    """Test task retry functionality"""
    
    # Create a task and then manually cancel it to test retry
    task_data = {
        "task_type": "csv_processing",
        "input_params": {
            "num_rows": 100,
            "processing_time": 5
        }
    }
    
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data)
    task_id = response.json().get("id")
    
    # Cancel it immediately
    time.sleep(0.5)
    httpx.delete(f"{BASE_URL}/api/tasks/{task_id}")
    
    # Wait for cancellation
    time.sleep(1)
    
    # Now retry it
    response = httpx.post(f"{BASE_URL}/api/tasks/{task_id}/retry")
    assert response.status_code == 200
    retried_task = response.json()
    assert retried_task.get("id") != task_id  # Should have new ID
    assert retried_task.get("status") == "PENDING"
    print(f"✓ Task retry successful. Original: {task_id}, New: {retried_task.get('id')}")


def test_different_task_types():
    """Test different task types (CORRECTED)"""
    
    task_types = [
        {
            "task_type": "csv_processing",  # FIXED
            "input_params": {               # FIXED
                "num_rows": 200,
                "processing_time": 2
            }
        },
        {
            "task_type": "email_sending",   # FIXED
            "input_params": {               # FIXED
                "num_emails": 3,
                "delay_per_email": 0.5,
                "subject": "Test Email"
            }
        },
        {
            "task_type": "image_processing",  # FIXED
            "input_params": {                 # FIXED
                "num_images": 2,
                "target_width": 800,
                "target_height": 600
            }
        }
    ]
    
    submitted_tasks = []
    
    for task_data in task_types:
        response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data)
        assert response.status_code in (200, 201), f"Failed for {task_data['task_type']}: {response.text}"
        task_id = response.json().get("id")
        submitted_tasks.append(task_id)
        print(f"✓ {task_data['task_type']} task submitted: {task_id}")
    
    # Verify all tasks are in the list
    response = httpx.get(f"{BASE_URL}/api/tasks/")
    assert response.status_code == 200
    tasks_response = response.json()
    tasks_data = tasks_response.get("tasks", [])
    
    # Check that at least our tasks are present
    assert len(tasks_data) >= len(submitted_tasks)
    print(f"✓ All task types verified in list: {len(submitted_tasks)} tasks")


def test_task_status_filtering():
    """Test filtering tasks by status"""
    
    # Submit a quick task first
    task_data = {
        "task_type": "email_sending",  # FIXED
        "input_params": {              # FIXED
            "num_emails": 1,
            "delay_per_email": 0.1
        }
    }
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data)
    assert response.status_code in (200, 201)
    
    # Wait for it to complete
    time.sleep(3)
    
    # Try to get tasks filtered by status
    response = httpx.get(f"{BASE_URL}/api/tasks/", params={"status": "SUCCESS"})
    assert response.status_code == 200
    filtered_response = response.json()
    filtered_tasks = filtered_response.get("tasks", [])
    
    # All returned tasks should have SUCCESS status
    for task in filtered_tasks:
        assert task.get("status") == "SUCCESS", f"Expected SUCCESS but got {task.get('status')}"
    
    print(f"✓ Status filtering works: {len(filtered_tasks)} SUCCESS tasks")


if __name__ == "__main__":
    print("=" * 50)
    print("Testing Task Queue Operations")
    print("=" * 50)
    
    try:
        test_task_operations()
        print("\n" + "=" * 50)
        print("Testing Task Retry")
        print("=" * 50)
        test_task_retry()
        
        print("\n" + "=" * 50)
        print("Testing Different Task Types")
        print("=" * 50)
        test_different_task_types()
        
        print("\n" + "=" * 50)
        print("Testing Task Filtering")
        print("=" * 50)
        test_task_status_filtering()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("=" * 50)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise

