"""
Celery Configuration

Celery app configuration for async task processing.
"""

from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "movie_recap_pipeline",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.preprocessing",
        "app.workers.transcription", 
        "app.workers.alignment",
        "app.workers.assembly",
        "app.workers.moderation"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=["json"],
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_default_queue="default",
    task_routes={
        "app.workers.preprocessing.*": {"queue": "preprocessing"},
        "app.workers.transcription.*": {"queue": "transcription"},
        "app.workers.alignment.*": {"queue": "alignment"},
        "app.workers.assembly.*": {"queue": "assembly"},
        "app.workers.moderation.*": {"queue": "moderation"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_compression="gzip",
    result_compression="gzip",
)

# Task retry configuration
celery_app.conf.task_annotations = {
    "*": {
        "rate_limit": "10/s",
        "retry_kwargs": {"max_retries": 3, "countdown": 60},
    },
    "app.workers.transcription.*": {
        "rate_limit": "2/s",  # More resource intensive
        "soft_time_limit": 3600,  # 1 hour
        "time_limit": 3900,  # 65 minutes
    },
    "app.workers.assembly.*": {
        "rate_limit": "1/s",  # Video processing is intensive
        "soft_time_limit": 7200,  # 2 hours
        "time_limit": 7500,  # 2 hours 5 minutes
    }
}

if __name__ == "__main__":
    celery_app.start()