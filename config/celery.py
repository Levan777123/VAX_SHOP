import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('vax_shop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-low-stock-report': {
        'task': 'apps.shop.tasks.send_low_stock_report',
        'schedule': crontab(hour=9, minute=0),
    },
}
