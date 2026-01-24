@echo off
echo Running Backend Tests...
cd backend
if not exist .venv (
    echo Creating virtual environment...
    uv venv --python 3.12
    call .venv\Scripts\activate
    uv pip install -r requirements.txt
) else (
    call .venv\Scripts\activate
)
cd ..
pytest tests/test_auth.py -v
pause

