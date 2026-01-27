import asyncio
import uuid
from typing import Dict, Optional
from datetime import datetime, timezone
from models import Task, TaskStatus, TaskType
from storage import TaskStorage
from task_workers import TaskWorkers

class TaskQueue:
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.queue: asyncio.Queue = asyncio.Queue()
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.workers = TaskWorkers()
        self.worker_task: Optional[asyncio.Task] = None
    
    async def start_worker(self):
        self.worker_task = asyncio.create_task(self._process_queue())
    
    async def stop_worker(self):
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
    
    async def _process_queue(self):
        while True:
            try:
                task_id = await self.queue.get()
                task = await self.storage.get_task(task_id)
                
                if task and task.status == TaskStatus.PENDING:
                    task_handle = asyncio.create_task(self._execute_task(task_id))
                    self.running_tasks[task_id] = task_handle
                
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing queue: {e}")
    
    async def _progress_callback(self, task_id: str, progress: int):
        await self.storage.update_task_status(
            task_id,
            TaskStatus.RUNNING,
            progress=progress
        )
    
    async def _execute_task(self, task_id: str):
        task = await self.storage.get_task(task_id)
        if not task or task.status == TaskStatus.CANCELLED:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            return
        
        try:
            await self.storage.update_task_status(
                task_id,
                TaskStatus.RUNNING,
                started_at=datetime.now(timezone.utc),
                progress=0
            )
            
            result = None
            if task.task_type == TaskType.DATA_PROCESSING:
                result = await self.workers.data_processing_task(
                    task_id,
                    task.result_data or {},
                    self._progress_callback,
                    self.storage
                )
            elif task.task_type == TaskType.EMAIL_SIMULATION:
                result = await self.workers.email_simulation_task(
                    task_id,
                    task.result_data or {},
                    self._progress_callback,
                    self.storage
                )
            elif task.task_type == TaskType.IMAGE_PROCESSING:
                result = await self.workers.image_processing_task(
                    task_id,
                    task.result_data or {},
                    self._progress_callback,
                    self.storage
                )
            
            task = await self.storage.get_task(task_id)
            if task and task.status != TaskStatus.CANCELLED:
                await self.storage.update_task_status(
                    task_id,
                    TaskStatus.SUCCESS,
                    completed_at=datetime.now(timezone.utc),
                    result_data=result,
                    progress=100
                )
        
        except asyncio.CancelledError:
            task = await self.storage.get_task(task_id)
            if task and task.status != TaskStatus.CANCELLED:
                await self.storage.update_task_status(
                    task_id,
                    TaskStatus.CANCELLED,
                    completed_at=datetime.now(timezone.utc)
                )
            raise
        except Exception as e:
            task = await self.storage.get_task(task_id)
            if task and task.status != TaskStatus.CANCELLED:
                await self.storage.update_task_status(
                    task_id,
                    TaskStatus.FAILED,
                    completed_at=datetime.now(timezone.utc),
                    error_message=str(e)
                )
        finally:
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
    
    async def submit_task(self, task_type: TaskType, parameters: Dict) -> Task:
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            result_data=parameters
        )
        
        await self.storage.create_task(task)
        await self.queue.put(task_id)
        
        return task
    
    async def cancel_task(self, task_id: str) -> bool:
        task = await self.storage.get_task(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            await self.storage.update_task_status(
                task_id,
                TaskStatus.CANCELLED,
                completed_at=datetime.now(timezone.utc)
            )
            
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
            
            return True
        
        return False
    
    async def retry_task(self, task_id: str) -> Optional[Task]:
        task = await self.storage.get_task(task_id)
        if not task or task.status != TaskStatus.FAILED:
            return None
        
        new_task_id = str(uuid.uuid4())
        new_task = Task(
            id=new_task_id,
            task_type=task.task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            result_data=task.result_data
        )
        
        await self.storage.create_task(new_task)
        await self.queue.put(new_task_id)
        
        return new_task
