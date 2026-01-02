#!/bin/bash
echo "Installing test dependencies..."
cd tests
pip install -r requirements.txt
cd ..
pip install -r backend/requirements.txt
echo ""
echo "Running test suite..."
python -m pytest tests/test_api.py -v

