@echo off
echo Installing test dependencies...
pip install -r tests\requirements.txt
pip install -r backend\requirements.txt
echo.
echo Running tests...
pytest tests\test_notes_api.py -v
pause
