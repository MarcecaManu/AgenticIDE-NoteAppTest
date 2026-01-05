@echo off
echo Starting Celery Worker...
celery -A celery_app worker --loglevel=info --pool=solo

