"""
Task worker implementations for different task types
"""
import asyncio
import json
import random
from datetime import datetime
from typing import Dict, Any
from backend.database import get_db
from backend.models import Task


class TaskWorker:
    """Base class for task workers"""
    
    @staticmethod
    async def update_task_progress(task_id: str, progress: float, status: str = None):
        """Update task progress in database"""
        # Try to get db_session_maker from task_queue if available (for testing)
        try:
            from backend.task_queue import task_queue
            if task_queue.db_session_maker:
                db = task_queue.db_session_maker()
                try:
                    task = db.query(Task).filter(Task.id == task_id).first()
                    if task:
                        task.progress = progress
                        if status:
                            task.status = status
                        db.commit()
                finally:
                    db.close()
                return
        except Exception:
            pass
        
        # Default to normal database
        with get_db() as db:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.progress = progress
                if status:
                    task.status = status
                db.commit()


class DataProcessingWorker(TaskWorker):
    """Worker for data processing tasks (CSV analysis simulation)"""
    
    @staticmethod
    async def execute(task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate CSV data processing task
        Takes 10-30 seconds with progress updates
        """
        rows = parameters.get("rows", 1000)
        processing_time = random.uniform(10, 30)
        chunks = 10
        chunk_duration = processing_time / chunks
        
        results = {
            "rows_processed": 0,
            "summary": {},
            "errors": 0
        }
        
        for i in range(chunks):
            # Simulate processing chunk
            await asyncio.sleep(chunk_duration)
            
            rows_in_chunk = rows // chunks
            results["rows_processed"] += rows_in_chunk
            
            # Update progress
            progress = ((i + 1) / chunks) * 100
            await DataProcessingWorker.update_task_progress(task_id, progress)
        
        # Generate summary statistics
        results["summary"] = {
            "total_rows": rows,
            "valid_rows": int(rows * 0.95),
            "invalid_rows": int(rows * 0.05),
            "average_value": round(random.uniform(50, 150), 2),
            "min_value": round(random.uniform(1, 50), 2),
            "max_value": round(random.uniform(150, 200), 2)
        }
        results["errors"] = int(rows * 0.05)
        
        return results


class EmailSimulationWorker(TaskWorker):
    """Worker for email sending simulation"""
    
    @staticmethod
    async def execute(task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate sending emails with delays
        """
        recipients = parameters.get("recipients", [])
        email_count = len(recipients) if recipients else parameters.get("count", 5)
        
        results = {
            "sent": 0,
            "failed": 0,
            "recipients": []
        }
        
        for i in range(email_count):
            # Simulate sending email (1-3 seconds per email)
            await asyncio.sleep(random.uniform(1, 3))
            
            # 90% success rate
            success = random.random() < 0.9
            
            if success:
                results["sent"] += 1
                results["recipients"].append({
                    "email": recipients[i] if recipients else f"user{i+1}@example.com",
                    "status": "sent",
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                results["failed"] += 1
                results["recipients"].append({
                    "email": recipients[i] if recipients else f"user{i+1}@example.com",
                    "status": "failed",
                    "error": "SMTP connection timeout"
                })
            
            # Update progress
            progress = ((i + 1) / email_count) * 100
            await EmailSimulationWorker.update_task_progress(task_id, progress)
        
        return results


class ImageProcessingWorker(TaskWorker):
    """Worker for image processing simulation"""
    
    @staticmethod
    async def execute(task_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate image resize/convert operations
        """
        image_count = parameters.get("count", 3)
        operation = parameters.get("operation", "resize")
        
        results = {
            "processed": 0,
            "failed": 0,
            "images": []
        }
        
        for i in range(image_count):
            # Simulate processing image (2-5 seconds per image)
            await asyncio.sleep(random.uniform(2, 5))
            
            # 95% success rate
            success = random.random() < 0.95
            
            if success:
                results["processed"] += 1
                results["images"].append({
                    "filename": f"image_{i+1}.jpg",
                    "original_size": f"{random.randint(1000, 3000)}x{random.randint(1000, 3000)}",
                    "new_size": f"{random.randint(500, 1000)}x{random.randint(500, 1000)}",
                    "operation": operation,
                    "status": "success"
                })
            else:
                results["failed"] += 1
                results["images"].append({
                    "filename": f"image_{i+1}.jpg",
                    "status": "failed",
                    "error": "Invalid image format"
                })
            
            # Update progress
            progress = ((i + 1) / image_count) * 100
            await ImageProcessingWorker.update_task_progress(task_id, progress)
        
        return results


# Task type mapping
TASK_WORKERS = {
    "data_processing": DataProcessingWorker,
    "email_simulation": EmailSimulationWorker,
    "image_processing": ImageProcessingWorker
}

