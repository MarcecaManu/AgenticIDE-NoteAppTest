@echo off
echo Starting Real-time Chat Backend...
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

