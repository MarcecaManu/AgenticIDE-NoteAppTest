#!/usr/bin/env python3
"""
Verify that the setup is correct and all tasks are registered
"""
import sys
import os

def check_imports():
    """Check if all modules can be imported"""
    print("Checking imports...")
    try:
        from celery_app import celery_app
        print("[OK] celery_app imported successfully")
        
        from tasks import process_csv_data, send_emails, process_images
        print("[OK] tasks imported successfully")
        
        from database import init_db, TaskModel
        print("[OK] database imported successfully")
        
        from main import app
        print("[OK] FastAPI app imported successfully")
        
        return True
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

def check_celery_tasks():
    """Check if Celery tasks are registered"""
    print("\nChecking Celery task registration...")
    try:
        from celery_app import celery_app
        
        registered_tasks = list(celery_app.tasks.keys())
        print(f"Found {len(registered_tasks)} registered tasks:")
        
        expected_tasks = [
            'tasks.process_csv_data',
            'tasks.send_emails', 
            'tasks.process_images'
        ]
        
        for task_name in registered_tasks:
            if not task_name.startswith('celery.'):
                print(f"  - {task_name}")
        
        # Check if our tasks are registered
        all_found = True
        for expected in expected_tasks:
            if expected not in registered_tasks:
                print(f"[ERROR] Missing task: {expected}")
                all_found = False
        
        if all_found:
            print("[OK] All expected tasks are registered")
            return True
        else:
            print("[ERROR] Some tasks are missing")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error checking tasks: {e}")
        return False

def check_redis():
    """Check Redis connection"""
    print("\nChecking Redis connection...")
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        print("[OK] Redis is running and accessible")
        return True
    except ImportError:
        print("[ERROR] redis package not installed (pip install redis)")
        return False
    except Exception as e:
        print(f"[ERROR] Cannot connect to Redis: {e}")
        return False

def check_database():
    """Check database connection"""
    print("\nChecking database...")
    try:
        from database import init_db, SessionLocal, TaskModel
        init_db()
        db = SessionLocal()
        count = db.query(TaskModel).count()
        db.close()
        print(f"[OK] Database initialized ({count} tasks in database)")
        return True
    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        return False

def main():
    print("=" * 50)
    print("Task Queue System - Setup Verification")
    print("=" * 50)
    print()
    
    results = []
    results.append(check_imports())
    results.append(check_redis())
    results.append(check_database())
    results.append(check_celery_tasks())
    
    print("\n" + "=" * 50)
    if all(results):
        print("[SUCCESS] ALL CHECKS PASSED - System is ready!")
        print("\nYou can now start:")
        print("1. Celery worker: celery -A celery_app worker --loglevel=info --pool=solo")
        print("2. FastAPI server: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        sys.exit(0)
    else:
        print("[FAILED] SOME CHECKS FAILED - Please fix the issues above")
        sys.exit(1)

if __name__ == "__main__":
    main()

