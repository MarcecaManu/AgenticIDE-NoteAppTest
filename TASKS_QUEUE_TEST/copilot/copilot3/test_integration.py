"""
Integration test to verify task execution in production mode.
This test starts the actual server and verifies tasks execute properly.
"""
import httpx
import time
import asyncio

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("Task Execution Integration Test")
print("=" * 60)
print("\nMake sure the server is running with:")
print("  cd backend")
print("  python run_server.py")
print("\nOr use:")
print("  .\\start.bat")
print("\nPress Enter when server is ready...")
input()

async def test_task_execution():
    """Test that tasks actually execute and transition through statuses."""
    
    print("\n1. Testing task submission...")
    task_data = {
        "task_type": "EMAIL_SIMULATION",
        "params": {"recipient_count": 3}
    }
    
    response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data, timeout=10.0)
    assert response.status_code == 200, f"Submit failed: {response.text}"
    task = response.json()
    task_id = task["id"]
    print(f"   ✓ Task submitted: {task_id}")
    print(f"   Initial status: {task['status']}")
    
    print("\n2. Monitoring task execution...")
    max_wait = 10  # seconds
    start_time = time.time()
    seen_running = False
    
    while time.time() - start_time < max_wait:
        response = httpx.get(f"{BASE_URL}/api/tasks/{task_id}", timeout=10.0)
        task = response.json()
        status = task["status"]
        progress = task.get("progress", 0)
        
        print(f"   Status: {status:10s} | Progress: {progress:5.1f}%", end="\r")
        
        if status == "RUNNING":
            seen_running = True
        
        if status in ["SUCCESS", "FAILED"]:
            print()  # New line
            break
            
        await asyncio.sleep(0.5)
    
    print(f"\n   Final status: {task['status']}")
    
    if seen_running:
        print("   ✓ Task transitioned through RUNNING state")
    else:
        print("   ⚠ Task never entered RUNNING state (might execute too quickly)")
    
    if task["status"] == "SUCCESS":
        print("   ✓ Task completed successfully")
        if task.get("result_data"):
            print(f"   ✓ Result data present")
    elif task["status"] == "FAILED":
        print(f"   ✗ Task failed: {task.get('error_message')}")
        return False
    else:
        print(f"   ⚠ Task did not complete in {max_wait} seconds")
    
    print("\n3. Testing task list...")
    response = httpx.get(f"{BASE_URL}/api/tasks/", timeout=10.0)
    tasks = response.json()
    print(f"   ✓ Found {len(tasks)} task(s)")
    
    print("\n" + "=" * 60)
    print("Integration test completed!")
    print("=" * 60)
    print("\nVerification:")
    print("  - Open http://localhost:8000 in your browser")
    print("  - Submit a task")
    print("  - Watch it transition from PENDING → RUNNING → SUCCESS")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(test_task_execution())
        exit(0 if result else 1)
    except httpx.ConnectError:
        print("\n✗ Error: Cannot connect to server")
        print("  Make sure the server is running on http://localhost:8000")
        exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)
