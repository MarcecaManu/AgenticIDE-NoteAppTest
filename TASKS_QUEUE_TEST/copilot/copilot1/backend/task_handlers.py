"""Task handlers for different task types."""
import asyncio
import random
from typing import Dict, Any, Callable
from .models import Task, TaskStatus
import csv
import io


class TaskHandlers:
    """Collection of task handlers for different task types."""
    
    @staticmethod
    async def data_processing_task(task: Task, progress_callback: Callable[[float], None]) -> Dict[str, Any]:
        """
        Simulate data processing (CSV analysis).
        Takes 10-30 seconds with progress updates.
        """
        parameters = task.parameters
        num_rows = parameters.get('num_rows', 1000)
        processing_time = parameters.get('processing_time', random.randint(10, 30))
        
        # Simulate CSV data analysis
        rows_processed = 0
        total_sum = 0
        max_value = 0
        min_value = float('inf')
        
        steps = 100
        rows_per_step = num_rows // steps
        sleep_time = processing_time / steps
        
        for step in range(steps):
            # Simulate processing a batch of rows
            await asyncio.sleep(sleep_time)
            
            batch_size = rows_per_step if step < steps - 1 else (num_rows - rows_processed)
            
            # Generate and "process" random data
            for _ in range(batch_size):
                value = random.randint(1, 1000)
                total_sum += value
                max_value = max(max_value, value)
                min_value = min(min_value, value)
                rows_processed += 1
            
            # Update progress
            progress = ((step + 1) / steps) * 100
            progress_callback(progress)
        
        # Return results
        return {
            'rows_processed': rows_processed,
            'total_sum': total_sum,
            'average': total_sum / rows_processed if rows_processed > 0 else 0,
            'max_value': max_value,
            'min_value': min_value,
            'processing_time': processing_time
        }
    
    @staticmethod
    async def email_simulation_task(task: Task, progress_callback: Callable[[float], None]) -> Dict[str, Any]:
        """
        Simulate sending emails with delays.
        """
        parameters = task.parameters
        num_emails = parameters.get('num_emails', 10)
        delay_per_email = parameters.get('delay_per_email', 1.0)
        
        sent_emails = []
        failed_emails = []
        
        for i in range(num_emails):
            email_address = f"user{i+1}@example.com"
            
            # Simulate sending email
            await asyncio.sleep(delay_per_email)
            
            # Simulate occasional failures (10% chance)
            if random.random() < 0.1:
                failed_emails.append({
                    'email': email_address,
                    'error': 'Simulated delivery failure'
                })
            else:
                sent_emails.append({
                    'email': email_address,
                    'subject': parameters.get('subject', 'Test Email'),
                    'sent_at': asyncio.get_event_loop().time()
                })
            
            # Update progress
            progress = ((i + 1) / num_emails) * 100
            progress_callback(progress)
        
        return {
            'total_emails': num_emails,
            'sent_successfully': len(sent_emails),
            'failed': len(failed_emails),
            'sent_emails': sent_emails[:5],  # Return first 5 for brevity
            'failed_emails': failed_emails
        }
    
    @staticmethod
    async def image_processing_task(task: Task, progress_callback: Callable[[float], None]) -> Dict[str, Any]:
        """
        Simulate image processing (resize/convert).
        """
        parameters = task.parameters
        num_images = parameters.get('num_images', 5)
        target_size = parameters.get('target_size', '800x600')
        output_format = parameters.get('output_format', 'PNG')
        
        processed_images = []
        
        for i in range(num_images):
            image_name = f"image_{i+1}.jpg"
            
            # Simulate image processing (takes 2-4 seconds per image)
            processing_time = random.uniform(2, 4)
            
            # Simulate progress within this image
            substeps = 10
            for substep in range(substeps):
                await asyncio.sleep(processing_time / substeps)
                
                # Update overall progress
                image_progress = (i + (substep + 1) / substeps) / num_images
                progress_callback(image_progress * 100)
            
            # Simulate processing result
            original_size = random.randint(500000, 2000000)  # bytes
            new_size = int(original_size * random.uniform(0.4, 0.7))
            
            processed_images.append({
                'original_name': image_name,
                'output_name': f"{image_name.rsplit('.', 1)[0]}.{output_format.lower()}",
                'original_size': original_size,
                'new_size': new_size,
                'compression_ratio': f"{(1 - new_size/original_size) * 100:.1f}%",
                'dimensions': target_size
            })
        
        return {
            'total_images': num_images,
            'processed_successfully': len(processed_images),
            'output_format': output_format,
            'target_size': target_size,
            'processed_images': processed_images,
            'total_size_saved': sum(img['original_size'] - img['new_size'] for img in processed_images)
        }
