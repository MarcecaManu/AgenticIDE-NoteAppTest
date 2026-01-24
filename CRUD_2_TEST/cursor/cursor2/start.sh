#!/bin/bash

echo "Starting Note Manager Application..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
echo ""
echo "Starting FastAPI server..."
echo "Open your browser at: http://localhost:8000"
echo ""
uvicorn backend.main:app --reload

