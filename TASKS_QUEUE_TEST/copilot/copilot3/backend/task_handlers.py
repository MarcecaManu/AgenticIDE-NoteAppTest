"""Task handlers for different task types."""
import asyncio
import random
import json
from typing import Dict, Any, Callable
from datetime import datetime


async def data_processing_task(task_id: str, params: Dict[str, Any], update_progress: Callable) -> Dict[str, Any]:
    """
    Simulate data processing task (CSV analysis).
    
    Args:
        task_id: Task identifier
        params: Input parameters (e.g., file_size, complexity)
        update_progress: Callback to update task progress
        
    Returns:
        Task result data
    """
    file_size = params.get("file_size", 1000)
    complexity = params.get("complexity", "medium")
    
    # Simulate processing time based on complexity
    duration_map = {"low": 10, "medium": 20, "high": 30}
    total_duration = duration_map.get(complexity, 20)
    
    rows_processed = 0
    total_rows = file_size
    
    # Simulate processing in chunks
    chunks = 10
    for i in range(chunks):
        await asyncio.sleep(total_duration / chunks)
        
        rows_processed += total_rows // chunks
        progress = ((i + 1) / chunks) * 100
        await update_progress(task_id, progress)
        
        # Simulate random errors (5% chance)
        if random.random() < 0.05:
            raise Exception(f"Data processing error at row {rows_processed}")
    
    # Generate mock results
    result = {
        "rows_processed": total_rows,
        "columns_analyzed": random.randint(5, 15),
        "null_values_found": random.randint(0, 100),
        "duplicate_rows": random.randint(0, 50),
        "summary_stats": {
            "mean": round(random.uniform(10, 100), 2),
            "median": round(random.uniform(10, 100), 2),
            "std_dev": round(random.uniform(5, 20), 2),
        },
        "processing_time_seconds": total_duration,
        "completed_at": datetime.utcnow().isoformat(),
    }
    
    return result


async def email_simulation_task(task_id: str, params: Dict[str, Any], update_progress: Callable) -> Dict[str, Any]:
    """
    Simulate email sending task.
    
    Args:
        task_id: Task identifier
        params: Input parameters (e.g., recipient_count, template)
        update_progress: Callback to update task progress
        
    Returns:
        Task result data
    """
    recipient_count = params.get("recipient_count", 10)
    template = params.get("template", "default")
    
    sent_count = 0
    failed_count = 0
    
    for i in range(recipient_count):
        # Simulate sending time per email
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Simulate random failures (10% chance)
        if random.random() < 0.1:
            failed_count += 1
        else:
            sent_count += 1
        
        progress = ((i + 1) / recipient_count) * 100
        await update_progress(task_id, progress)
    
    result = {
        "total_recipients": recipient_count,
        "successfully_sent": sent_count,
        "failed": failed_count,
        "template_used": template,
        "send_rate_per_second": round(recipient_count / (recipient_count * 1.0), 2),
        "completed_at": datetime.utcnow().isoformat(),
    }
    
    return result


async def image_processing_task(task_id: str, params: Dict[str, Any], update_progress: Callable) -> Dict[str, Any]:
    """
    Simulate image processing task (resize/convert).
    
    Args:
        task_id: Task identifier
        params: Input parameters (e.g., image_count, operation)
        update_progress: Callback to update task progress
        
    Returns:
        Task result data
    """
    image_count = params.get("image_count", 5)
    operation = params.get("operation", "resize")
    target_size = params.get("target_size", "1920x1080")
    
    processed_images = []
    
    for i in range(image_count):
        # Simulate processing time per image
        await asyncio.sleep(random.uniform(2, 4))
        
        # Simulate random errors (5% chance)
        if random.random() < 0.05:
            raise Exception(f"Failed to process image {i + 1}")
        
        processed_images.append({
            "image_id": f"img_{i + 1}",
            "original_size": f"{random.randint(2000, 4000)}x{random.randint(2000, 4000)}",
            "processed_size": target_size,
            "operation": operation,
            "file_size_kb": random.randint(100, 500),
        })
        
        progress = ((i + 1) / image_count) * 100
        await update_progress(task_id, progress)
    
    result = {
        "total_images": image_count,
        "successfully_processed": len(processed_images),
        "operation": operation,
        "target_size": target_size,
        "processed_images": processed_images,
        "total_size_kb": sum(img["file_size_kb"] for img in processed_images),
        "completed_at": datetime.utcnow().isoformat(),
    }
    
    return result


# Task handler registry
TASK_HANDLERS = {
    "DATA_PROCESSING": data_processing_task,
    "EMAIL_SIMULATION": email_simulation_task,
    "IMAGE_PROCESSING": image_processing_task,
}
