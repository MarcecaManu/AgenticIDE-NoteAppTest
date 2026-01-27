import asyncio
import random
from typing import Dict, Any
from datetime import datetime
from models import TaskStatus

class TaskWorkers:
    @staticmethod
    async def data_processing_task(task_id: str, parameters: Dict[str, Any], progress_callback, storage) -> Dict[str, Any]:
        rows = parameters.get('rows', 1000)
        processing_time = parameters.get('processing_time', 15)
        
        task = await storage.get_task(task_id)
        if task and task.status == TaskStatus.CANCELLED:
            raise asyncio.CancelledError()
        
        await progress_callback(task_id, 10)
        await asyncio.sleep(processing_time * 0.2)
        
        task = await storage.get_task(task_id)
        if task and task.status == TaskStatus.CANCELLED:
            raise asyncio.CancelledError()
        
        await progress_callback(task_id, 30)
        total_sum = sum(range(rows))
        await asyncio.sleep(processing_time * 0.3)
        
        task = await storage.get_task(task_id)
        if task and task.status == TaskStatus.CANCELLED:
            raise asyncio.CancelledError()
        
        await progress_callback(task_id, 60)
        average = total_sum / rows if rows > 0 else 0
        await asyncio.sleep(processing_time * 0.3)
        
        task = await storage.get_task(task_id)
        if task and task.status == TaskStatus.CANCELLED:
            raise asyncio.CancelledError()
        
        await progress_callback(task_id, 90)
        await asyncio.sleep(processing_time * 0.2)
        
        result = {
            'rows_processed': rows,
            'total_sum': total_sum,
            'average': average,
            'processing_time': processing_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    @staticmethod
    async def email_simulation_task(task_id: str, parameters: Dict[str, Any], progress_callback, storage) -> Dict[str, Any]:
        recipient_count = parameters.get('recipient_count', 10)
        delay_per_email = parameters.get('delay_per_email', 1)
        
        sent_emails = []
        
        for i in range(recipient_count):
            task = await storage.get_task(task_id)
            if task and task.status == TaskStatus.CANCELLED:
                raise asyncio.CancelledError()
            
            progress = int((i + 1) / recipient_count * 100)
            await progress_callback(task_id, progress)
            
            email_data = {
                'recipient': f'user{i+1}@example.com',
                'subject': parameters.get('subject', 'Test Email'),
                'sent_at': datetime.utcnow().isoformat(),
                'status': 'sent'
            }
            sent_emails.append(email_data)
            
            await asyncio.sleep(delay_per_email)
        
        result = {
            'total_sent': recipient_count,
            'emails': sent_emails,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
    
    @staticmethod
    async def image_processing_task(task_id: str, parameters: Dict[str, Any], progress_callback, storage) -> Dict[str, Any]:
        image_count = parameters.get('image_count', 5)
        operation = parameters.get('operation', 'resize')
        processing_time = parameters.get('processing_time', 10)
        
        processed_images = []
        
        for i in range(image_count):
            task = await storage.get_task(task_id)
            if task and task.status == TaskStatus.CANCELLED:
                raise asyncio.CancelledError()
            
            progress = int((i + 1) / image_count * 100)
            await progress_callback(task_id, progress)
            
            image_data = {
                'image_name': f'image_{i+1}.jpg',
                'operation': operation,
                'original_size': f'{random.randint(800, 2000)}x{random.randint(600, 1500)}',
                'new_size': f'{random.randint(400, 800)}x{random.randint(300, 600)}',
                'processed_at': datetime.utcnow().isoformat()
            }
            processed_images.append(image_data)
            
            await asyncio.sleep(processing_time / image_count)
        
        result = {
            'total_processed': image_count,
            'operation': operation,
            'images': processed_images,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return result
