@echo off
echo Running Task Queue Tests...
cd tests
pytest test_tasks.py -v
pause
