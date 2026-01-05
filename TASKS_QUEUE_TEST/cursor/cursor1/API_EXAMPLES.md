# API Examples

Complete examples for interacting with the Task Queue API.

## Base URL

```
http://localhost:8000/api
```

## 1. Submit Tasks

### CSV Processing Task

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "csv_processing",
    "input_params": {
      "num_rows": 1000,
      "processing_time": 15
    }
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "csv_processing",
  "status": "PENDING",
  "created_at": "2024-01-05T10:30:00",
  "started_at": null,
  "completed_at": null,
  "result_data": null,
  "error_message": null,
  "progress": 0.0,
  "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
}
```

### Email Sending Task

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "email_sending",
    "input_params": {
      "num_emails": 10,
      "subject": "Monthly Newsletter",
      "delay_per_email": 1.0
    }
  }'
```

**Response:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "task_type": "email_sending",
  "status": "PENDING",
  "created_at": "2024-01-05T10:31:00",
  "started_at": null,
  "completed_at": null,
  "result_data": null,
  "error_message": null,
  "progress": 0.0,
  "input_params": "{\"num_emails\": 10, \"subject\": \"Monthly Newsletter\", \"delay_per_email\": 1.0}"
}
```

### Image Processing Task

```bash
curl -X POST "http://localhost:8000/api/tasks/submit" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "image_processing",
    "input_params": {
      "num_images": 5,
      "target_width": 800,
      "target_height": 600
    }
  }'
```

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "task_type": "image_processing",
  "status": "PENDING",
  "created_at": "2024-01-05T10:32:00",
  "started_at": null,
  "completed_at": null,
  "result_data": null,
  "error_message": null,
  "progress": 0.0,
  "input_params": "{\"num_images\": 5, \"target_width\": 800, \"target_height\": 600}"
}
```

## 2. List All Tasks

```bash
curl "http://localhost:8000/api/tasks/"
```

**Response:**
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "task_type": "csv_processing",
      "status": "SUCCESS",
      "created_at": "2024-01-05T10:30:00",
      "started_at": "2024-01-05T10:30:05",
      "completed_at": "2024-01-05T10:30:20",
      "result_data": "{\"total_rows\": 1000, \"processed_rows\": 1000, \"statistics\": {...}}",
      "error_message": null,
      "progress": 100.0,
      "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
    }
  ],
  "total": 1
}
```

## 3. Filter Tasks

### By Status

```bash
# Get all running tasks
curl "http://localhost:8000/api/tasks/?status=RUNNING"

# Get all failed tasks
curl "http://localhost:8000/api/tasks/?status=FAILED"

# Get all successful tasks
curl "http://localhost:8000/api/tasks/?status=SUCCESS"
```

### By Task Type

```bash
# Get all CSV processing tasks
curl "http://localhost:8000/api/tasks/?task_type=csv_processing"

# Get all email sending tasks
curl "http://localhost:8000/api/tasks/?task_type=email_sending"

# Get all image processing tasks
curl "http://localhost:8000/api/tasks/?task_type=image_processing"
```

### Combined Filters

```bash
# Get running CSV processing tasks
curl "http://localhost:8000/api/tasks/?status=RUNNING&task_type=csv_processing"
```

### With Pagination

```bash
# Get first 10 tasks
curl "http://localhost:8000/api/tasks/?limit=10&offset=0"

# Get next 10 tasks
curl "http://localhost:8000/api/tasks/?limit=10&offset=10"
```

## 4. Get Specific Task

```bash
curl "http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**Response (Running Task):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "csv_processing",
  "status": "RUNNING",
  "created_at": "2024-01-05T10:30:00",
  "started_at": "2024-01-05T10:30:05",
  "completed_at": null,
  "result_data": null,
  "error_message": null,
  "progress": 45.5,
  "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
}
```

**Response (Completed Task):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "csv_processing",
  "status": "SUCCESS",
  "created_at": "2024-01-05T10:30:00",
  "started_at": "2024-01-05T10:30:05",
  "completed_at": "2024-01-05T10:30:20",
  "result_data": "{\"total_rows\": 1000, \"processed_rows\": 1000, \"statistics\": {\"sum\": 523456, \"avg\": 523.456, \"min\": 1, \"max\": 1000}}",
  "error_message": null,
  "progress": 100.0,
  "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
}
```

**Response (Failed Task):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "task_type": "csv_processing",
  "status": "FAILED",
  "created_at": "2024-01-05T10:30:00",
  "started_at": "2024-01-05T10:30:05",
  "completed_at": "2024-01-05T10:30:08",
  "result_data": null,
  "error_message": "Database connection error",
  "progress": 23.0,
  "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
}
```

## 5. Cancel Task

```bash
curl -X DELETE "http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000"
```

**Response:**
```json
{
  "message": "Task cancelled successfully",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (Cannot Cancel):**
```json
{
  "detail": "Cannot cancel task with status: SUCCESS"
}
```

## 6. Retry Task

```bash
curl -X POST "http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000/retry"
```

**Response:**
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "task_type": "csv_processing",
  "status": "PENDING",
  "created_at": "2024-01-05T10:35:00",
  "started_at": null,
  "completed_at": null,
  "result_data": null,
  "error_message": null,
  "progress": 0.0,
  "input_params": "{\"num_rows\": 1000, \"processing_time\": 15}"
}
```

**Error Response (Cannot Retry):**
```json
{
  "detail": "Cannot retry task with status: SUCCESS. Only FAILED or CANCELLED tasks can be retried."
}
```

## 7. Health Check

```bash
curl "http://localhost:8000/api/health"
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-05T10:40:00.123456"
}
```

## Python Examples

### Using `requests` library

```python
import requests
import time

# Base URL
BASE_URL = "http://localhost:8000/api"

# Submit a task
response = requests.post(
    f"{BASE_URL}/tasks/submit",
    json={
        "task_type": "csv_processing",
        "input_params": {
            "num_rows": 1000,
            "processing_time": 15
        }
    }
)
task = response.json()
task_id = task["id"]
print(f"Submitted task: {task_id}")

# Poll for completion
while True:
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    task = response.json()
    
    print(f"Status: {task['status']}, Progress: {task['progress']}%")
    
    if task["status"] in ["SUCCESS", "FAILED", "CANCELLED"]:
        break
    
    time.sleep(2)

# Print results
if task["status"] == "SUCCESS":
    print(f"Task completed! Results: {task['result_data']}")
else:
    print(f"Task {task['status']}: {task.get('error_message', 'No error message')}")
```

### Retry Failed Tasks

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get all failed tasks
response = requests.get(f"{BASE_URL}/tasks/?status=FAILED")
failed_tasks = response.json()["tasks"]

print(f"Found {len(failed_tasks)} failed tasks")

# Retry each one
for task in failed_tasks:
    response = requests.post(f"{BASE_URL}/tasks/{task['id']}/retry")
    new_task = response.json()
    print(f"Retried task {task['id']} as {new_task['id']}")
```

### Cancel All Pending Tasks

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Get all pending tasks
response = requests.get(f"{BASE_URL}/tasks/?status=PENDING")
pending_tasks = response.json()["tasks"]

print(f"Found {len(pending_tasks)} pending tasks")

# Cancel each one
for task in pending_tasks:
    response = requests.delete(f"{BASE_URL}/tasks/{task['id']}")
    if response.status_code == 200:
        print(f"Cancelled task {task['id']}")
    else:
        print(f"Failed to cancel task {task['id']}: {response.json()}")
```

## JavaScript Examples

### Using `fetch` API

```javascript
const BASE_URL = 'http://localhost:8000/api';

// Submit a task
async function submitTask() {
    const response = await fetch(`${BASE_URL}/tasks/submit`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            task_type: 'csv_processing',
            input_params: {
                num_rows: 1000,
                processing_time: 15
            }
        })
    });
    
    const task = await response.json();
    console.log('Submitted task:', task.id);
    return task.id;
}

// Monitor task progress
async function monitorTask(taskId) {
    const interval = setInterval(async () => {
        const response = await fetch(`${BASE_URL}/tasks/${taskId}`);
        const task = await response.json();
        
        console.log(`Status: ${task.status}, Progress: ${task.progress}%`);
        
        if (['SUCCESS', 'FAILED', 'CANCELLED'].includes(task.status)) {
            clearInterval(interval);
            console.log('Task finished:', task);
        }
    }, 2000);
}

// Usage
const taskId = await submitTask();
await monitorTask(taskId);
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid task type. Must be one of: csv_processing, email_sending, image_processing"
}
```

### 404 Not Found
```json
{
  "detail": "Task not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "task_type"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting (Production)

In production, you should implement rate limiting:

```python
# Example with slowapi
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/tasks/submit")
@limiter.limit("10/minute")
async def submit_task(...):
    ...
```

Response when rate limited:
```json
{
  "error": "Rate limit exceeded. Try again in 30 seconds."
}
```

## Best Practices

1. **Always check response status codes**
2. **Handle network errors gracefully**
3. **Implement exponential backoff for retries**
4. **Use task IDs for tracking**
5. **Monitor task execution time**
6. **Implement timeouts on client side**
7. **Log all API interactions**
8. **Validate input parameters**
9. **Use HTTPS in production**
10. **Implement authentication for production**

