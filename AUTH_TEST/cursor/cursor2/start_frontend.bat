@echo off
echo Starting Frontend Server...
cd frontend
echo Frontend will be available at http://localhost:8080
python -m http.server 8080

