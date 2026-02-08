"""
Celery application for background task scheduling
Handles automated price optimization for all stores
"""

from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

# Create Celery app
celery_app = Celery(
    'salla_price_optimizer',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['scheduler.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Riyadh',  # Saudi Arabia timezone
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3000,  # 50 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Periodic task schedule
celery_app.conf.beat_schedule = {
    # Run every 6 hours
    'optimize-all-stores-6h': {
        'task': 'scheduler.tasks.optimize_all_stores',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    
    # Check for stores needing optimization every hour
    'check-stores-hourly': {
        'task': 'scheduler.tasks.check_and_optimize_stores',
        'schedule': crontab(minute=0),  # Every hour
    },
    
    # Refresh expired tokens daily
    'refresh-tokens-daily': {
        'task': 'scheduler.tasks.refresh_expired_tokens',
        'schedule': crontab(minute=0, hour=2),  # 2 AM daily
    },
    
    # Cleanup old data weekly
    'cleanup-old-data-weekly': {
        'task': 'scheduler.tasks.cleanup_old_data',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Sunday 3 AM
    },
}

if __name__ == '__main__':
    celery_app.start()
