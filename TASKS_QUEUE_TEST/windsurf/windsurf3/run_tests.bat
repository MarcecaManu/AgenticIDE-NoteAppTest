@echo off
echo Running Test Suite...
cd tests
pytest test_api.py -v
pause
