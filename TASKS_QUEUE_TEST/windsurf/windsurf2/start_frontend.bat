@echo off
echo Starting Task Queue Frontend...
cd frontend
python -m http.server 8080
