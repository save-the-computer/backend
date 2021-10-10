from __future__ import absolute_import
import os

# About celery, see https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
from celery import Celery
from celery.schedules import crontab


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'save_the_computer.settings')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app = Celery('products')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps. (tasks.py)
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'Collect': {
        'task': 'products.tasks.collect',
        'schedule': crontab(hour=5, minute=0),
    },
    'Download One Thumbnail': {
        'task': 'products.tasks.download_one_thumbnail',
        'schedule': 60 * 5, # every 5 minutes
    }
}