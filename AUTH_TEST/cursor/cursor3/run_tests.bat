@echo off
echo Running pytest tests...
echo.
call .\.venv\Scripts\activate
python -m pytest tests/test_auth.py -v
echo.
pause

