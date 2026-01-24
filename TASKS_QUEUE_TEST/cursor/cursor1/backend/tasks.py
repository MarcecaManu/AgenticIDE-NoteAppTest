import time
import json
import random
from datetime import datetime
from celery_app import celery_app
from database import SessionLocal, TaskModel
from io import BytesIO
from PIL import Image


def update_task_status(task_id: str, **kwargs):
    """Update task status in database"""
    db = SessionLocal()
    try:
        task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
        if task:
            for key, value in kwargs.items():
                setattr(task, key, value)
            db.commit()
    finally:
        db.close()


@celery_app.task(bind=True)
def process_csv_data(self, task_id: str, input_params: dict):
    """
    Simulate CSV data processing task (10-30 seconds)
    Processes rows and calculates statistics
    """
    try:
        # Update to RUNNING
        update_task_status(
            task_id,
            status="RUNNING",
            started_at=datetime.utcnow()
        )
        
        # Simulate CSV processing
        num_rows = input_params.get("num_rows", 1000)
        processing_time = input_params.get("processing_time", 15)  # seconds
        
        results = {
            "total_rows": num_rows,
            "processed_rows": 0,
            "statistics": {
                "sum": 0,
                "avg": 0,
                "min": float('inf'),
                "max": float('-inf')
            }
        }
        
        # Process in chunks to show progress
        chunk_size = 100
        chunks = num_rows // chunk_size
        sleep_per_chunk = processing_time / chunks
        
        for i in range(chunks):
            # Simulate processing
            time.sleep(sleep_per_chunk)
            
            # Generate random data for this chunk
            chunk_data = [random.randint(1, 1000) for _ in range(chunk_size)]
            results["processed_rows"] += chunk_size
            results["statistics"]["sum"] += sum(chunk_data)
            results["statistics"]["min"] = min(results["statistics"]["min"], min(chunk_data))
            results["statistics"]["max"] = max(results["statistics"]["max"], max(chunk_data))
            
            # Update progress
            progress = (i + 1) / chunks * 100
            update_task_status(task_id, progress=progress)
        
        # Calculate final statistics
        results["statistics"]["avg"] = results["statistics"]["sum"] / num_rows
        
        # Mark as SUCCESS
        update_task_status(
            task_id,
            status="SUCCESS",
            completed_at=datetime.utcnow(),
            result_data=json.dumps(results),
            progress=100.0
        )
        
        return results
        
    except Exception as e:
        update_task_status(
            task_id,
            status="FAILED",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        raise


@celery_app.task(bind=True)
def send_emails(self, task_id: str, input_params: dict):
    """
    Simulate sending emails with delays
    """
    try:
        update_task_status(
            task_id,
            status="RUNNING",
            started_at=datetime.utcnow()
        )
        
        num_emails = input_params.get("num_emails", 10)
        delay_per_email = input_params.get("delay_per_email", 1)  # seconds
        
        sent_emails = []
        
        for i in range(num_emails):
            # Simulate sending email
            time.sleep(delay_per_email)
            
            email_data = {
                "to": f"user{i+1}@example.com",
                "subject": input_params.get("subject", "Test Email"),
                "sent_at": datetime.utcnow().isoformat(),
                "status": "delivered"
            }
            sent_emails.append(email_data)
            
            # Update progress
            progress = (i + 1) / num_emails * 100
            update_task_status(task_id, progress=progress)
        
        results = {
            "total_emails": num_emails,
            "sent_successfully": len(sent_emails),
            "failed": 0,
            "emails": sent_emails
        }
        
        update_task_status(
            task_id,
            status="SUCCESS",
            completed_at=datetime.utcnow(),
            result_data=json.dumps(results),
            progress=100.0
        )
        
        return results
        
    except Exception as e:
        update_task_status(
            task_id,
            status="FAILED",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        raise


@celery_app.task(bind=True)
def process_images(self, task_id: str, input_params: dict):
    """
    Simulate image processing (resize/convert)
    """
    try:
        update_task_status(
            task_id,
            status="RUNNING",
            started_at=datetime.utcnow()
        )
        
        num_images = input_params.get("num_images", 5)
        target_width = input_params.get("target_width", 800)
        target_height = input_params.get("target_height", 600)
        
        processed_images = []
        
        for i in range(num_images):
            # Simulate image processing
            time.sleep(2)  # Each image takes 2 seconds
            
            # Create a dummy image and resize it
            img = Image.new('RGB', (1920, 1080), color=(random.randint(0, 255), 
                                                         random.randint(0, 255), 
                                                         random.randint(0, 255)))
            img_resized = img.resize((target_width, target_height))
            
            # Get image info
            buffer = BytesIO()
            img_resized.save(buffer, format='JPEG')
            size_kb = len(buffer.getvalue()) / 1024
            
            image_data = {
                "original_name": f"image_{i+1}.jpg",
                "processed_name": f"image_{i+1}_resized.jpg",
                "original_size": "1920x1080",
                "new_size": f"{target_width}x{target_height}",
                "file_size_kb": round(size_kb, 2),
                "processed_at": datetime.utcnow().isoformat()
            }
            processed_images.append(image_data)
            
            # Update progress
            progress = (i + 1) / num_images * 100
            update_task_status(task_id, progress=progress)
        
        results = {
            "total_images": num_images,
            "processed_successfully": len(processed_images),
            "failed": 0,
            "images": processed_images
        }
        
        update_task_status(
            task_id,
            status="SUCCESS",
            completed_at=datetime.utcnow(),
            result_data=json.dumps(results),
            progress=100.0
        )
        
        return results
        
    except Exception as e:
        update_task_status(
            task_id,
            status="FAILED",
            completed_at=datetime.utcnow(),
            error_message=str(e)
        )
        raise

