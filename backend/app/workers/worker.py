"""
Celery Worker Entry Point
Run with: celery -A app.workers.worker worker --loglevel=info
"""
from app.workers.celery_app import celery_app

# Import tasks to register them
from app.workers import tasks

if __name__ == "__main__":
    celery_app.start()
