"""
Celery Application Configuration
"""
from celery import Celery
from app.core.config import settings

# Create Celery application
celery_app = Celery(
    "nashama_vision",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
    task_soft_time_limit=3300,  # 55 minutes soft timeout
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing (can be expanded for multiple queues)
celery_app.conf.task_routes = {
    "app.workers.tasks.process_video_task": {"queue": "video_processing"},
    "app.workers.tasks.analytics_computation_task": {"queue": "analytics"},
}
