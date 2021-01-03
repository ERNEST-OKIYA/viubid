import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'QuickBid.settings')

app = Celery('quickbid')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()