import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedback_report.settings')

app = Celery('feedback_report')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
