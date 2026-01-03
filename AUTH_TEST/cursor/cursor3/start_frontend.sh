#!/bin/bash
echo "Starting Frontend Server..."
echo ""
echo "The frontend will be available at http://localhost:3000"
echo ""
source .venv/bin/activate
cd frontend
python3 -m http.server 3000

