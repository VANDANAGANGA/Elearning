# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'deactivate-old-schedules': {
        'task': 'accounts.tasks.deactivate_old_schedules',
        'schedule': crontab(hour=0, minute=0),  # Run daily at midnight
    },
}
