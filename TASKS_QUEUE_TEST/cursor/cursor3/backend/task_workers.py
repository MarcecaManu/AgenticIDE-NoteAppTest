"""Task worker implementations for different task types."""
import asyncio
import random
import time
from typing import Dict, Any, Callable
from datetime import datetime


class TaskWorker:
    """Base class for task workers."""
    
    def __init__(self, task_id: str, parameters: Dict[str, Any], progress_callback: Callable):
        self.task_id = task_id
        self.parameters = parameters
        self.progress_callback = progress_callback
        self.cancelled = False
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the task. To be overridden by subclasses."""
        raise NotImplementedError
    
    def cancel(self):
        """Cancel the task."""
        self.cancelled = True


class DataProcessingWorker(TaskWorker):
    """Worker for data processing tasks (CSV analysis simulation)."""
    
    async def execute(self) -> Dict[str, Any]:
        """Simulate CSV data processing with progress updates."""
        rows = self.parameters.get("rows", 1000)
        processing_time = self.parameters.get("processing_time", 15)
        
        result = {
            "total_rows": rows,
            "processed_rows": 0,
            "statistics": {
                "sum": 0,
                "average": 0,
                "min": 0,
                "max": 0
            },
            "processing_time_seconds": 0
        }
        
        start_time = time.time()
        step_duration = processing_time / 10
        
        # Simulate processing in 10 steps
        for step in range(10):
            if self.cancelled:
                raise Exception("Task was cancelled")
            
            await asyncio.sleep(step_duration)
            
            # Update progress
            progress = (step + 1) * 10
            self.progress_callback(self.task_id, progress)
            
            # Simulate processing
            processed = int(rows * (step + 1) / 10)
            result["processed_rows"] = processed
        
        # Generate fake statistics
        result["statistics"] = {
            "sum": random.randint(10000, 100000),
            "average": random.uniform(50, 500),
            "min": random.randint(1, 50),
            "max": random.randint(500, 1000)
        }
        result["processing_time_seconds"] = time.time() - start_time
        
        return result


class EmailSimulationWorker(TaskWorker):
    """Worker for email simulation tasks."""
    
    async def execute(self) -> Dict[str, Any]:
        """Simulate sending emails with delays."""
        recipient_count = self.parameters.get("recipient_count", 5)
        delay_per_email = self.parameters.get("delay_per_email", 2)
        
        result = {
            "total_emails": recipient_count,
            "sent_emails": 0,
            "failed_emails": 0,
            "recipients": []
        }
        
        for i in range(recipient_count):
            if self.cancelled:
                raise Exception("Task was cancelled")
            
            await asyncio.sleep(delay_per_email)
            
            # Simulate random failures (5% chance)
            success = random.random() > 0.05
            
            recipient = {
                "email": f"user{i+1}@example.com",
                "status": "sent" if success else "failed",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            result["recipients"].append(recipient)
            if success:
                result["sent_emails"] += 1
            else:
                result["failed_emails"] += 1
            
            # Update progress
            progress = int((i + 1) / recipient_count * 100)
            self.progress_callback(self.task_id, progress)
        
        return result


class ImageProcessingWorker(TaskWorker):
    """Worker for image processing tasks."""
    
    async def execute(self) -> Dict[str, Any]:
        """Simulate image processing (resize/convert)."""
        image_count = self.parameters.get("image_count", 10)
        operation = self.parameters.get("operation", "resize")
        target_size = self.parameters.get("target_size", "800x600")
        
        result = {
            "total_images": image_count,
            "processed_images": 0,
            "operation": operation,
            "target_size": target_size,
            "images": []
        }
        
        for i in range(image_count):
            if self.cancelled:
                raise Exception("Task was cancelled")
            
            # Simulate processing time
            await asyncio.sleep(random.uniform(1, 3))
            
            image_result = {
                "filename": f"image_{i+1}.jpg",
                "original_size": f"{random.randint(1000, 3000)}x{random.randint(1000, 3000)}",
                "new_size": target_size,
                "size_reduction_percent": random.randint(40, 80),
                "processing_time_ms": random.randint(100, 500)
            }
            
            result["images"].append(image_result)
            result["processed_images"] += 1
            
            # Update progress
            progress = int((i + 1) / image_count * 100)
            self.progress_callback(self.task_id, progress)
        
        return result


# Task worker registry
TASK_WORKERS = {
    "DATA_PROCESSING": DataProcessingWorker,
    "EMAIL_SIMULATION": EmailSimulationWorker,
    "IMAGE_PROCESSING": ImageProcessingWorker
}


def get_worker(task_type: str, task_id: str, parameters: Dict[str, Any], 
               progress_callback: Callable) -> TaskWorker:
    """Get the appropriate worker for a task type."""
    worker_class = TASK_WORKERS.get(task_type)
    if not worker_class:
        raise ValueError(f"Unknown task type: {task_type}")
    return worker_class(task_id, parameters, progress_callback)


