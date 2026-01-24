#!/bin/bash
echo "Running Backend Tests..."
cd backend
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python 3.12
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    source .venv/bin/activate
fi
cd ..
pytest tests/test_auth.py -v

