#!/usr/bin/env python3
"""Test that all imports work without circular dependency issues"""

print("Testing imports...")

try:
    print("1. Importing celery_app...", end=" ")
    from celery_app import celery_app
    print("OK")
    
    print("2. Importing tasks...", end=" ")
    from tasks import process_csv_data, send_emails, process_images
    print("OK")
    
    print("3. Importing database...", end=" ")
    from database import init_db, TaskModel
    print("OK")
    
    print("4. Importing main...", end=" ")
    from main import app
    print("OK")
    
    print("\n[SUCCESS] All imports successful! No circular dependency.")
    print("\nRegistered Celery tasks:")
    for task_name in celery_app.tasks.keys():
        if not task_name.startswith('celery.'):
            print(f"  - {task_name}")
    
except ImportError as e:
    print(f"\n[ERROR] Import Error: {e}")
    exit(1)
except Exception as e:
    print(f"\n[ERROR] Error: {e}")
    exit(1)

