#!/bin/bash
echo "================================================"
echo "Task Queue System - Fix and Restart"
echo "================================================"
echo ""

echo "Step 1: Clearing Redis queue..."
python3 clear_redis.py
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to clear Redis. Make sure Redis is running."
    exit 1
fi
echo ""

echo "Step 2: Verifying setup..."
python3 verify_setup.py
if [ $? -ne 0 ]; then
    echo "ERROR: Setup verification failed. Please check the errors above."
    exit 1
fi
echo ""

echo "================================================"
echo "SUCCESS! System is ready."
echo "================================================"
echo ""
echo "Now you need to start the services in separate terminals:"
echo ""
echo "Terminal 1 - Celery Worker:"
echo "  cd backend"
echo "  celery -A celery_app worker --loglevel=info"
echo ""
echo "Terminal 2 - FastAPI Server:"
echo "  cd backend"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Then open: http://localhost:8000"
echo ""

