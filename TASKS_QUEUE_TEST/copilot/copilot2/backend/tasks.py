"""
Celery task definitions for background processing.
Implements data processing, email simulation, and image processing tasks.
"""

from celery import Task
from backend.celery_app import celery_app
from backend.database import SessionLocal, TaskDB
from datetime import datetime
import time
import random
import json
import csv
from io import StringIO


class DatabaseTask(Task):
    """Base task class that updates database status"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Update database on task failure"""
        db = SessionLocal()
        try:
            task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if task:
                task.status = "FAILED"
                task.completed_at = datetime.utcnow()
                task.error_message = str(exc)
                db.commit()
        finally:
            db.close()

    def on_success(self, retval, task_id, args, kwargs):
        """Update database on task success"""
        db = SessionLocal()
        try:
            task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
            if task:
                task.status = "SUCCESS"
                task.completed_at = datetime.utcnow()
                task.progress = 100
                db.commit()
        finally:
            db.close()


def update_task_progress(task_id: str, progress: int, status: str = None):
    """Update task progress in database"""
    db = SessionLocal()
    try:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task:
            task.progress = progress
            if status:
                task.status = status
            if status == "RUNNING" and not task.started_at:
                task.started_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, base=DatabaseTask, name="backend.tasks.data_processing_task")
def data_processing_task(self, task_id: str, input_data: dict):
    """
    Data processing task - simulates CSV analysis that takes 10-30 seconds.
    Processes data in chunks and reports progress.
    """
    update_task_progress(task_id, 0, "RUNNING")
    
    # Check if task was cancelled
    db = SessionLocal()
    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
    if task and task.status == "CANCELLED":
        db.close()
        return {"status": "cancelled"}
    db.close()
    
    # Simulate processing time (10-30 seconds)
    processing_time = random.randint(10, 30)
    rows = input_data.get("rows", 1000)
    
    results = {
        "total_rows": rows,
        "processed_rows": 0,
        "statistics": {},
        "processing_time_seconds": processing_time
    }
    
    # Process in chunks to report progress
    chunks = 10
    chunk_size = rows // chunks
    
    for i in range(chunks):
        # Check for cancellation
        db = SessionLocal()
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task and task.status == "CANCELLED":
            db.close()
            return {"status": "cancelled"}
        db.close()
        
        # Simulate processing
        time.sleep(processing_time / chunks)
        results["processed_rows"] += chunk_size
        
        # Update progress
        progress = int((i + 1) * 100 / chunks)
        update_task_progress(task_id, progress)
    
    # Generate statistics
    results["statistics"] = {
        "mean": round(random.uniform(50, 100), 2),
        "median": round(random.uniform(40, 90), 2),
        "std_dev": round(random.uniform(10, 25), 2),
        "min": round(random.uniform(0, 30), 2),
        "max": round(random.uniform(100, 200), 2)
    }
    
    # Store result
    db = SessionLocal()
    try:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task:
            task.result_data = json.dumps(results)
            db.commit()
    finally:
        db.close()
    
    return results


@celery_app.task(bind=True, base=DatabaseTask, name="backend.tasks.email_simulation_task")
def email_simulation_task(self, task_id: str, input_data: dict):
    """
    Email simulation task - simulates sending emails with delays.
    """
    update_task_progress(task_id, 0, "RUNNING")
    
    recipient_count = input_data.get("recipient_count", 10)
    delay_per_email = input_data.get("delay_per_email", 1)  # seconds
    
    results = {
        "total_emails": recipient_count,
        "sent_emails": 0,
        "failed_emails": 0,
        "recipients": []
    }
    
    for i in range(recipient_count):
        # Check for cancellation
        db = SessionLocal()
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task and task.status == "CANCELLED":
            db.close()
            return {"status": "cancelled"}
        db.close()
        
        # Simulate sending email
        time.sleep(delay_per_email)
        
        # Randomly simulate some failures (10% chance)
        success = random.random() > 0.1
        
        recipient = {
            "email": f"user{i+1}@example.com",
            "status": "sent" if success else "failed",
            "timestamp": datetime.utcnow().isoformat()
        }
        results["recipients"].append(recipient)
        
        if success:
            results["sent_emails"] += 1
        else:
            results["failed_emails"] += 1
        
        # Update progress
        progress = int((i + 1) * 100 / recipient_count)
        update_task_progress(task_id, progress)
    
    # Store result
    db = SessionLocal()
    try:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task:
            task.result_data = json.dumps(results)
            db.commit()
    finally:
        db.close()
    
    return results


@celery_app.task(bind=True, base=DatabaseTask, name="backend.tasks.image_processing_task")
def image_processing_task(self, task_id: str, input_data: dict):
    """
    Image processing task - simulates image resize/conversion.
    """
    update_task_progress(task_id, 0, "RUNNING")
    
    image_count = input_data.get("image_count", 5)
    operation = input_data.get("operation", "resize")  # resize, convert, compress
    target_size = input_data.get("target_size", "800x600")
    
    results = {
        "total_images": image_count,
        "processed_images": 0,
        "operation": operation,
        "target_size": target_size,
        "images": []
    }
    
    # Each image takes 2-5 seconds to process
    for i in range(image_count):
        # Check for cancellation
        db = SessionLocal()
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task and task.status == "CANCELLED":
            db.close()
            return {"status": "cancelled"}
        db.close()
        
        # Simulate processing time
        processing_time = random.uniform(2, 5)
        time.sleep(processing_time)
        
        image_result = {
            "filename": f"image_{i+1}.jpg",
            "original_size": f"{random.randint(1920, 3840)}x{random.randint(1080, 2160)}",
            "new_size": target_size,
            "original_size_kb": random.randint(500, 3000),
            "new_size_kb": random.randint(100, 800),
            "processing_time": round(processing_time, 2)
        }
        results["images"].append(image_result)
        results["processed_images"] += 1
        
        # Update progress
        progress = int((i + 1) * 100 / image_count)
        update_task_progress(task_id, progress)
    
    # Calculate total savings
    total_original = sum(img["original_size_kb"] for img in results["images"])
    total_new = sum(img["new_size_kb"] for img in results["images"])
    results["total_size_reduction_percent"] = round((1 - total_new / total_original) * 100, 2)
    
    # Store result
    db = SessionLocal()
    try:
        task = db.query(TaskDB).filter(TaskDB.id == task_id).first()
        if task:
            task.result_data = json.dumps(results)
            db.commit()
    finally:
        db.close()
    
    return results
