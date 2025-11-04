"""
Celery application configuration for FileGuard
Handles async tasks like antivirus scanning, email notifications, etc.
"""
from celery import Celery
from core.config import settings

# Create Celery app
celery_app = Celery(
    "fileguard",
    broker=settings.get_celery_broker_url,
    backend=settings.get_celery_result_backend
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # Results expire after 1 hour
)

# Auto-discover tasks from modules
celery_app.autodiscover_tasks(['tasks'])
