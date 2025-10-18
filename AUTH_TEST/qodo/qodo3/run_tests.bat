@echo off
echo Installing test dependencies...
cd tests
python -m pip install -r requirements.txt
echo.
echo Running authentication API tests...
echo.
pytest test_auth_api.py -v
pause