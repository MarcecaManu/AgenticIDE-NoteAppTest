@echo off
echo Installing test dependencies...
cd tests
pip install -r requirements.txt
echo.
echo Running authentication API tests...
pytest test_auth_api.py -v
pause