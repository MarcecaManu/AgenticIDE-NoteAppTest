@echo off
echo Installing test dependencies...
cd tests
python -m pip install -r requirements.txt
cd ..
python -m pip install -r backend\requirements.txt
echo.
echo Running test suite...
python -m pytest tests/test_api.py -v
pause

