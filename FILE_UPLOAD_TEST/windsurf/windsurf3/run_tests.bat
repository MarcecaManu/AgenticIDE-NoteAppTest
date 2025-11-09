@echo off
echo Running File Upload & Management Tests...
pip install -r backend/requirements.txt
python -m pytest tests/ -v
pause
