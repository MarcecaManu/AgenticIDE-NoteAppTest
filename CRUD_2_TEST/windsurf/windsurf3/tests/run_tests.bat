@echo off
echo Installing test dependencies...
pip install -r requirements.txt
pip install -r ..\backend\requirements.txt
echo.
echo Running tests...
pytest test_api.py -v
pause
