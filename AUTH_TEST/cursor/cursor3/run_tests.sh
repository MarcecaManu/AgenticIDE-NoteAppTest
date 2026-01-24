#!/bin/bash
echo "Running pytest tests..."
echo ""
source .venv/bin/activate
python -m pytest tests/test_auth.py -v

