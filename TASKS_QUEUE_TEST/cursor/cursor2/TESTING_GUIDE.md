# Testing Guide

Complete guide for testing the Task Queue & Background Processing System.

## Test Suite Overview

The project includes **16 comprehensive automated tests** covering all major functionality.

### Test Files

1. **`tests/test_api.py`** - API endpoint tests (16 tests)
2. **`tests/test_task_workers.py`** - Worker implementation tests (6 tests)

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_api.py -v
pytest tests/test_task_workers.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_api.py::TestTaskSubmission -v
```

### Run Specific Test
```bash
pytest tests/test_api.py::TestTaskSubmission::test_submit_data_processing_task -v
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view coverage report.

### Run with Coverage Report in Terminal
```bash
pytest --cov=backend --cov-report=term-missing
```

## Test Categories

### 1. Task Submission Tests

**Location**: `tests/test_api.py::TestTaskSubmission`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_submit_data_processing_task` | Submit data processing task | Valid submission returns task_id |
| `test_submit_email_simulation_task` | Submit email task | Email task creation works |
| `test_submit_image_processing_task` | Submit image task | Image task creation works |
| `test_submit_invalid_task_type` | Invalid task type | Returns 400 error |

**Run**:
```bash
pytest tests/test_api.py::TestTaskSubmission -v
```

### 2. Task Retrieval Tests

**Location**: `tests/test_api.py::TestTaskRetrieval`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_list_all_tasks` | List all tasks | Returns task list |
| `test_filter_tasks_by_status` | Filter by status | Status filtering works |
| `test_filter_tasks_by_type` | Filter by type | Type filtering works |
| `test_get_specific_task` | Get task details | Returns specific task |
| `test_get_nonexistent_task` | Get invalid task | Returns 404 |

**Run**:
```bash
pytest tests/test_api.py::TestTaskRetrieval -v
```

### 3. Task Cancellation Tests

**Location**: `tests/test_api.py::TestTaskCancellation`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_cancel_pending_task` | Cancel a task | Task status becomes CANCELLED |
| `test_cancel_nonexistent_task` | Cancel invalid task | Returns 404 |

**Run**:
```bash
pytest tests/test_api.py::TestTaskCancellation -v
```

### 4. Task Retry Tests

**Location**: `tests/test_api.py::TestTaskRetry`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_retry_failed_task` | Retry logic | Only FAILED tasks can be retried |
| `test_retry_nonexistent_task` | Retry invalid task | Returns 404 |

**Run**:
```bash
pytest tests/test_api.py::TestTaskRetry -v
```

### 5. Health Check Tests

**Location**: `tests/test_api.py::TestHealthCheck`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_health_check` | API health | Returns healthy status |

**Run**:
```bash
pytest tests/test_api.py::TestHealthCheck -v
```

### 6. Task Execution Tests

**Location**: `tests/test_api.py::TestTaskExecution`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_task_status_progression` | Status changes | Task progresses through states |
| `test_multiple_tasks_concurrent` | Concurrent execution | Multiple tasks work together |

**Run**:
```bash
pytest tests/test_api.py::TestTaskExecution -v
```

### 7. Worker Implementation Tests

**Location**: `tests/test_task_workers.py`

| Test | Description | What It Checks |
|------|-------------|----------------|
| `test_data_processing_execution` | Data worker | Processes data correctly |
| `test_data_processing_with_custom_rows` | Custom parameters | Handles different row counts |
| `test_email_simulation_execution` | Email worker | Sends emails correctly |
| `test_email_simulation_with_recipients` | Custom recipients | Handles recipient lists |
| `test_image_processing_execution` | Image worker | Processes images correctly |
| `test_image_processing_different_operations` | Different operations | Handles resize/convert/compress |

**Run**:
```bash
pytest tests/test_task_workers.py -v
```

## Manual Testing

### Test Task Submission

1. Start the server:
```bash
python run.py
```

2. Submit a task via curl:
```bash
curl -X POST http://localhost:8000/api/tasks/submit \
  -H "Content-Type: application/json" \
  -d '{"task_type": "data_processing", "parameters": {"rows": 1000}}'
```

Expected response:
```json
{
  "task_id": "uuid-here",
  "status": "submitted"
}
```

### Test Task Retrieval

```bash
curl http://localhost:8000/api/tasks/
```

Expected: JSON array of tasks

### Test Task Details

```bash
curl http://localhost:8000/api/tasks/{task_id}
```

Expected: JSON object with task details

### Test Task Cancellation

```bash
curl -X DELETE http://localhost:8000/api/tasks/{task_id}
```

Expected:
```json
{
  "status": "cancelled",
  "task_id": "uuid-here"
}
```

### Test Task Retry

```bash
curl -X POST http://localhost:8000/api/tasks/{task_id}/retry
```

Expected:
```json
{
  "status": "retried",
  "new_task_id": "new-uuid-here"
}
```

## Frontend Testing

### Manual UI Testing Checklist

1. **Task Submission**
   - [ ] Select each task type
   - [ ] Verify parameter forms change
   - [ ] Submit each task type
   - [ ] Verify success notification
   - [ ] Verify task appears in list

2. **Task Monitoring**
   - [ ] Verify tasks appear in list
   - [ ] Verify status badges are correct
   - [ ] Verify progress bars show for RUNNING tasks
   - [ ] Verify auto-refresh works (every 2 seconds)
   - [ ] Verify duration display

3. **Task Filtering**
   - [ ] Filter by each status
   - [ ] Filter by each task type
   - [ ] Combine filters
   - [ ] Verify refresh button works

4. **Task Details**
   - [ ] Click on a task
   - [ ] Verify modal opens
   - [ ] Verify all details shown
   - [ ] Verify parameters displayed
   - [ ] Verify results displayed (for completed tasks)
   - [ ] Close modal

5. **Task Actions**
   - [ ] Cancel a pending task
   - [ ] Verify cancellation confirmation
   - [ ] Retry a failed task
   - [ ] Verify new task created

## Performance Testing

### Load Testing

Test with multiple concurrent tasks:

```python
import asyncio
import httpx

async def submit_tasks(count):
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(count):
            task = client.post(
                "http://localhost:8000/api/tasks/submit",
                json={
                    "task_type": "email_simulation",
                    "parameters": {"count": 2}
                }
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Run
asyncio.run(submit_tasks(10))
```

### Stress Testing

Monitor system with many tasks:

```bash
# Submit 50 tasks
for i in {1..50}; do
  curl -X POST http://localhost:8000/api/tasks/submit \
    -H "Content-Type: application/json" \
    -d '{"task_type": "data_processing", "parameters": {"rows": 100}}' &
done
```

## Test Database

Tests use a separate test database (`test_tasks.db`) that is:
- Created before each test
- Cleaned up after each test
- Isolated from development database

## Continuous Integration

For CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=backend --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v2
```

## Debugging Failed Tests

### View detailed output
```bash
pytest -vv --tb=long
```

### Run with print statements
```bash
pytest -s
```

### Run specific test with debugging
```bash
pytest tests/test_api.py::TestTaskSubmission::test_submit_data_processing_task -vv -s
```

### Check test database
```bash
sqlite3 test_tasks.db
.tables
SELECT * FROM tasks;
```

## Expected Test Results

All tests should pass:

```
tests/test_api.py::TestTaskSubmission::test_submit_data_processing_task PASSED
tests/test_api.py::TestTaskSubmission::test_submit_email_simulation_task PASSED
tests/test_api.py::TestTaskSubmission::test_submit_image_processing_task PASSED
tests/test_api.py::TestTaskSubmission::test_submit_invalid_task_type PASSED
tests/test_api.py::TestTaskRetrieval::test_list_all_tasks PASSED
tests/test_api.py::TestTaskRetrieval::test_filter_tasks_by_status PASSED
tests/test_api.py::TestTaskRetrieval::test_filter_tasks_by_type PASSED
tests/test_api.py::TestTaskRetrieval::test_get_specific_task PASSED
tests/test_api.py::TestTaskRetrieval::test_get_nonexistent_task PASSED
tests/test_api.py::TestTaskCancellation::test_cancel_pending_task PASSED
tests/test_api.py::TestTaskCancellation::test_cancel_nonexistent_task PASSED
tests/test_api.py::TestTaskRetry::test_retry_failed_task PASSED
tests/test_api.py::TestTaskRetry::test_retry_nonexistent_task PASSED
tests/test_api.py::TestHealthCheck::test_health_check PASSED
tests/test_api.py::TestTaskExecution::test_task_status_progression PASSED
tests/test_api.py::TestTaskExecution::test_multiple_tasks_concurrent PASSED
tests/test_task_workers.py::TestDataProcessingWorker::test_data_processing_execution PASSED
tests/test_task_workers.py::TestDataProcessingWorker::test_data_processing_with_custom_rows PASSED
tests/test_task_workers.py::TestEmailSimulationWorker::test_email_simulation_execution PASSED
tests/test_task_workers.py::TestEmailSimulationWorker::test_email_simulation_with_recipients PASSED
tests/test_task_workers.py::TestImageProcessingWorker::test_image_processing_execution PASSED
tests/test_task_workers.py::TestImageProcessingWorker::test_image_processing_different_operations PASSED

======================== 22 passed in X.XXs ========================
```

## Troubleshooting

### Tests hang
- Check for infinite loops in async code
- Verify asyncio event loop is properly managed

### Database errors
- Ensure test database is cleaned up
- Check file permissions

### Import errors
- Verify you're in the project root
- Check PYTHONPATH includes project directory

### Async test errors
- Ensure pytest-asyncio is installed
- Check `pytest.ini` has `asyncio_mode = auto`

## Coverage Goals

Target coverage: **> 80%**

Check coverage:
```bash
pytest --cov=backend --cov-report=term-missing
```

Areas to focus on:
- All API endpoints
- All task workers
- Error handling paths
- Edge cases

## Next Steps

After all tests pass:
1. Review coverage report
2. Add tests for edge cases
3. Add integration tests
4. Add performance benchmarks
5. Set up CI/CD pipeline

Happy Testing! 🧪

