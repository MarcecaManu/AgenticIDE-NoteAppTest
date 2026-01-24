@echo off
echo Running Authentication Tests...
echo.
pytest tests/test_auth.py -v
echo.
pause

