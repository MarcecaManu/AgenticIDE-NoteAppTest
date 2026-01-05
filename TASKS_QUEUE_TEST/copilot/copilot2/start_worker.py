"""
Script to start the Celery worker.
Usage: python start_worker.py
"""

import sys
import os
from celery import Celery

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

if __name__ == "__main__":
    print("🔄 Starting Celery Worker...")
    print("⚠️  Make sure Redis is running!")
    print("\n📋 Available task types:")
    print("   - data_processing_task")
    print("   - email_simulation_task")
    print("   - image_processing_task\n")
    
    from backend.celery_app import celery_app
    
    # Start worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Required for Windows
        '--concurrency=4'
    ])
