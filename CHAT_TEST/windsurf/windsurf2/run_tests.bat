@echo off
echo Installing test dependencies...
cd tests
pip install -r requirements.txt
pip install -r ..\backend\requirements.txt
echo.
echo Running tests...
pytest test_chat.py -v
pause
