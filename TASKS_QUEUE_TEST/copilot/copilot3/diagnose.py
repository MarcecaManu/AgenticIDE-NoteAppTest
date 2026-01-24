"""Diagnostic script to check server status and worker health."""
import httpx
import sys

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if server is running and responsive."""
    print("Checking server health...")
    try:
        response = httpx.get(f"{BASE_URL}/api/health", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Server is running")
            print(f"  Status: {data['status']}")
            print(f"  Queue size: {data['queue_size']}")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except httpx.ConnectError:
        print("✗ Cannot connect to server")
        print("  Make sure the server is running:")
        print("  cd backend && python run_server.py")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def submit_test_task():
    """Submit a test task and check if it gets queued."""
    print("\nSubmitting test task...")
    try:
        task_data = {
            "task_type": "EMAIL_SIMULATION",
            "params": {"recipient_count": 2}
        }
        response = httpx.post(f"{BASE_URL}/api/tasks/submit", json=task_data, timeout=5.0)
        if response.status_code == 200:
            task = response.json()
            print(f"✓ Task submitted: {task['id']}")
            print(f"  Status: {task['status']}")
            print(f"  Type: {task['task_type']}")
            return task['id']
        else:
            print(f"✗ Failed to submit task: {response.status_code}")
            print(f"  {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Task Queue System - Diagnostic Check")
    print("=" * 60)
    print()
    
    if not check_server():
        sys.exit(1)
    
    task_id = submit_test_task()
    if not task_id:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Diagnostic check completed!")
    print("=" * 60)
    print("\nCheck the server console output for:")
    print("  [Server] Startup event triggered")
    print("  [Server] Database initialized")
    print("  [Server] Task worker started")
    print("  [TaskQueue] Worker started")
    print("  [TaskQueue] Task ... added to queue")
    print("  [TaskQueue] Got task from queue")
    print("  [TaskQueue] Executing task")
    print("\nIf you don't see these messages, the worker may not be running.")
    print("=" * 60)
