import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatgpt_parser.settings')

app = Celery('chatgpt_parser')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
