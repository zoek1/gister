import os

from celery import Celery

from gister import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gister.settings')
app = Celery('gister')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()