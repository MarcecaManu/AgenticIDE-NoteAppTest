"""Task worker tests."""
import pytest
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from task_workers import (
    DataProcessingWorker,
    EmailSimulationWorker,
    ImageProcessingWorker,
    get_worker
)


def progress_callback(task_id, progress):
    """Mock progress callback."""
    pass


@pytest.mark.asyncio
async def test_data_processing_worker():
    """Test 13: Data processing worker execution."""
    worker = DataProcessingWorker(
        task_id="test-1",
        parameters={"rows": 100, "processing_time": 1},
        progress_callback=progress_callback
    )
    
    result = await worker.execute()
    
    assert result["total_rows"] == 100
    assert result["processed_rows"] == 100
    assert "statistics" in result
    assert result["statistics"]["sum"] > 0
    assert result["processing_time_seconds"] >= 1


@pytest.mark.asyncio
async def test_email_simulation_worker():
    """Test 14: Email simulation worker execution."""
    worker = EmailSimulationWorker(
        task_id="test-2",
        parameters={"recipient_count": 3, "delay_per_email": 0.5},
        progress_callback=progress_callback
    )
    
    result = await worker.execute()
    
    assert result["total_emails"] == 3
    assert result["sent_emails"] + result["failed_emails"] == 3
    assert len(result["recipients"]) == 3
    assert all("email" in r for r in result["recipients"])


@pytest.mark.asyncio
async def test_image_processing_worker():
    """Test 15: Image processing worker execution."""
    worker = ImageProcessingWorker(
        task_id="test-3",
        parameters={
            "image_count": 5,
            "operation": "resize",
            "target_size": "800x600"
        },
        progress_callback=progress_callback
    )
    
    result = await worker.execute()
    
    assert result["total_images"] == 5
    assert result["processed_images"] == 5
    assert result["operation"] == "resize"
    assert len(result["images"]) == 5


@pytest.mark.asyncio
async def test_worker_cancellation():
    """Test 16: Worker cancellation."""
    worker = DataProcessingWorker(
        task_id="test-cancel",
        parameters={"rows": 1000, "processing_time": 10},
        progress_callback=progress_callback
    )
    
    # Cancel the worker after a short delay
    async def cancel_after_delay():
        await asyncio.sleep(0.5)
        worker.cancel()
    
    # Run both tasks concurrently
    cancel_task = asyncio.create_task(cancel_after_delay())
    
    with pytest.raises(Exception) as exc_info:
        await worker.execute()
    
    assert "cancelled" in str(exc_info.value).lower()
    await cancel_task


def test_get_worker_factory():
    """Test 17: Worker factory function."""
    # Test valid worker types
    worker1 = get_worker("DATA_PROCESSING", "test-1", {}, progress_callback)
    assert isinstance(worker1, DataProcessingWorker)
    
    worker2 = get_worker("EMAIL_SIMULATION", "test-2", {}, progress_callback)
    assert isinstance(worker2, EmailSimulationWorker)
    
    worker3 = get_worker("IMAGE_PROCESSING", "test-3", {}, progress_callback)
    assert isinstance(worker3, ImageProcessingWorker)
    
    # Test invalid worker type
    with pytest.raises(ValueError):
        get_worker("INVALID_TYPE", "test-4", {}, progress_callback)


