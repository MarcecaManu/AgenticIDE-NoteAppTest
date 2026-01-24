#!/usr/bin/env python3
"""
Clear Redis queue to remove old/invalid tasks
Run this if you see errors about unregistered tasks
"""
import redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    # Connect to Redis
    r = redis.from_url(REDIS_URL)
    
    # Flush the database
    r.flushdb()
    
    print("[SUCCESS] Redis queue cleared successfully!")
    print("You can now restart the Celery worker and FastAPI server.")
    
except redis.ConnectionError:
    print("[ERROR] Could not connect to Redis")
    print("Make sure Redis is running on localhost:6379")
except Exception as e:
    print(f"[ERROR] {e}")

