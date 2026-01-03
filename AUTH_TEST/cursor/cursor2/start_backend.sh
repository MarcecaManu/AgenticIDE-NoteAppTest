#!/bin/bash
echo "Starting FastAPI Backend..."
cd backend
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    uv venv --python 3.12
fi
source .venv/bin/activate
echo "Installing dependencies..."
uv pip install -r requirements.txt
echo "Starting server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000

