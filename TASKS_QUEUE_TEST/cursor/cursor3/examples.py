"""
Example scripts demonstrating how to use the Task Queue API programmatically.
"""
import requests
import time
import json

API_BASE = "http://localhost:8000/api"


def example_1_submit_data_processing_task():
    """Example 1: Submit a data processing task."""
    print("\n" + "="*60)
    print("Example 1: Submitting Data Processing Task")
    print("="*60)
    
    response = requests.post(f"{API_BASE}/tasks/submit", json={
        "task_type": "DATA_PROCESSING",
        "parameters": {
            "rows": 1000,
            "processing_time": 15
        }
    })
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Task submitted successfully!")
        print(f"Task ID: {task['id']}")
        print(f"Status: {task['status']}")
        print(f"Type: {task['task_type']}")
        return task['id']
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def example_2_submit_email_task():
    """Example 2: Submit an email simulation task."""
    print("\n" + "="*60)
    print("Example 2: Submitting Email Simulation Task")
    print("="*60)
    
    response = requests.post(f"{API_BASE}/tasks/submit", json={
        "task_type": "EMAIL_SIMULATION",
        "parameters": {
            "recipient_count": 5,
            "delay_per_email": 2
        }
    })
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Task submitted successfully!")
        print(f"Task ID: {task['id']}")
        print(f"Recipients: {task['parameters']['recipient_count']}")
        return task['id']
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def example_3_submit_image_task():
    """Example 3: Submit an image processing task."""
    print("\n" + "="*60)
    print("Example 3: Submitting Image Processing Task")
    print("="*60)
    
    response = requests.post(f"{API_BASE}/tasks/submit", json={
        "task_type": "IMAGE_PROCESSING",
        "parameters": {
            "image_count": 10,
            "operation": "resize",
            "target_size": "800x600"
        }
    })
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ Task submitted successfully!")
        print(f"Task ID: {task['id']}")
        print(f"Images to process: {task['parameters']['image_count']}")
        return task['id']
    else:
        print(f"❌ Error: {response.status_code}")
        return None


def example_4_monitor_task(task_id):
    """Example 4: Monitor task progress."""
    print("\n" + "="*60)
    print("Example 4: Monitoring Task Progress")
    print("="*60)
    print(f"Monitoring task: {task_id}")
    
    while True:
        response = requests.get(f"{API_BASE}/tasks/{task_id}")
        if response.status_code == 200:
            task = response.json()
            status = task['status']
            progress = task.get('progress', '0')
            
            print(f"\rStatus: {status} | Progress: {progress}%", end="", flush=True)
            
            if status in ['SUCCESS', 'FAILED', 'CANCELLED']:
                print()  # New line
                print(f"\nTask completed with status: {status}")
                
                if status == 'SUCCESS' and task.get('result_data'):
                    print("\nResults:")
                    print(json.dumps(task['result_data'], indent=2))
                elif status == 'FAILED':
                    print(f"\nError: {task.get('error_message')}")
                break
        else:
            print(f"\n❌ Error fetching task: {response.status_code}")
            break
        
        time.sleep(2)  # Poll every 2 seconds


def example_5_list_all_tasks():
    """Example 5: List all tasks."""
    print("\n" + "="*60)
    print("Example 5: Listing All Tasks")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/tasks/")
    if response.status_code == 200:
        tasks = response.json()
        print(f"Total tasks: {len(tasks)}\n")
        
        for i, task in enumerate(tasks[:10], 1):  # Show first 10
            print(f"{i}. {task['id'][:8]}... - {task['task_type']} - {task['status']}")
    else:
        print(f"❌ Error: {response.status_code}")


def example_6_filter_tasks_by_status():
    """Example 6: Filter tasks by status."""
    print("\n" + "="*60)
    print("Example 6: Filtering Tasks by Status")
    print("="*60)
    
    statuses = ['PENDING', 'RUNNING', 'SUCCESS', 'FAILED']
    
    for status in statuses:
        response = requests.get(f"{API_BASE}/tasks/?status={status}")
        if response.status_code == 200:
            tasks = response.json()
            print(f"{status}: {len(tasks)} tasks")
        else:
            print(f"❌ Error fetching {status} tasks")


def example_7_cancel_task(task_id):
    """Example 7: Cancel a task."""
    print("\n" + "="*60)
    print("Example 7: Cancelling a Task")
    print("="*60)
    print(f"Attempting to cancel task: {task_id}")
    
    response = requests.delete(f"{API_BASE}/tasks/{task_id}")
    if response.status_code == 200:
        print("✅ Task cancelled successfully!")
    else:
        print(f"❌ Error: {response.status_code}")
        if response.status_code == 400:
            print("Task may have already completed or cannot be cancelled.")


def example_8_batch_submit():
    """Example 8: Submit multiple tasks in batch."""
    print("\n" + "="*60)
    print("Example 8: Batch Task Submission")
    print("="*60)
    
    task_configs = [
        {"task_type": "DATA_PROCESSING", "parameters": {"rows": 500, "processing_time": 10}},
        {"task_type": "EMAIL_SIMULATION", "parameters": {"recipient_count": 3, "delay_per_email": 1}},
        {"task_type": "IMAGE_PROCESSING", "parameters": {"image_count": 5, "operation": "resize"}},
    ]
    
    task_ids = []
    for config in task_configs:
        response = requests.post(f"{API_BASE}/tasks/submit", json=config)
        if response.status_code == 200:
            task = response.json()
            task_ids.append(task['id'])
            print(f"✅ Submitted {config['task_type']}: {task['id'][:8]}...")
        else:
            print(f"❌ Failed to submit {config['task_type']}")
    
    print(f"\nTotal tasks submitted: {len(task_ids)}")
    return task_ids


def example_9_wait_for_completion(task_ids):
    """Example 9: Wait for multiple tasks to complete."""
    print("\n" + "="*60)
    print("Example 9: Waiting for Multiple Tasks")
    print("="*60)
    
    completed = set()
    
    while len(completed) < len(task_ids):
        for task_id in task_ids:
            if task_id in completed:
                continue
            
            response = requests.get(f"{API_BASE}/tasks/{task_id}")
            if response.status_code == 200:
                task = response.json()
                if task['status'] in ['SUCCESS', 'FAILED', 'CANCELLED']:
                    completed.add(task_id)
                    print(f"✅ Task {task_id[:8]}... completed with status: {task['status']}")
        
        if len(completed) < len(task_ids):
            print(f"Waiting... ({len(completed)}/{len(task_ids)} completed)")
            time.sleep(3)
    
    print("\n🎉 All tasks completed!")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("🚀 Task Queue System - API Examples")
    print("="*60)
    print("\nMake sure the server is running at http://localhost:8000")
    
    try:
        # Check if server is running
        response = requests.get(f"{API_BASE}/health")
        if response.status_code != 200:
            print("❌ Server is not responding. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        print("\nRun: python run.py")
        return
    
    print("✅ Server is running!\n")
    
    # Run examples
    choice = input("Choose example to run (1-9, or 'all'): ").strip()
    
    if choice == '1' or choice == 'all':
        task_id = example_1_submit_data_processing_task()
        if task_id and choice == '1':
            example_4_monitor_task(task_id)
    
    if choice == '2' or choice == 'all':
        task_id = example_2_submit_email_task()
        if task_id and choice == '2':
            example_4_monitor_task(task_id)
    
    if choice == '3' or choice == 'all':
        task_id = example_3_submit_image_task()
        if task_id and choice == '3':
            example_4_monitor_task(task_id)
    
    if choice == '4':
        task_id = input("Enter task ID to monitor: ").strip()
        example_4_monitor_task(task_id)
    
    if choice == '5' or choice == 'all':
        example_5_list_all_tasks()
    
    if choice == '6' or choice == 'all':
        example_6_filter_tasks_by_status()
    
    if choice == '7':
        task_id = input("Enter task ID to cancel: ").strip()
        example_7_cancel_task(task_id)
    
    if choice == '8' or choice == 'all':
        task_ids = example_8_batch_submit()
        if choice == '8':
            example_9_wait_for_completion(task_ids)
    
    if choice == '9':
        task_ids = input("Enter task IDs (comma-separated): ").strip().split(',')
        example_9_wait_for_completion([t.strip() for t in task_ids])
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()


