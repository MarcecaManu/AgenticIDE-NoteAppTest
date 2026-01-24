@echo off
echo ========================================
echo Running Task Queue Tests
echo ========================================
echo.

python -m pytest tests\test_api.py -v --tb=short

echo.
echo ========================================
echo Test execution completed
echo ========================================
pause
