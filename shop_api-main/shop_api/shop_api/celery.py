import os
import sys
from pathlib import Path

from celery import Celery
from celery.schedules import crontab

# Такой же трюк с sys.path, как в manage.py: apps 'product' и 'users'
# лежат в shop_api/ и импортируются как top-level пакеты.
sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_api.settings')

app = Celery('shop_api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['product', 'users'])

# Пример периодической задачи, запускаемой по расписанию через crontab.
app.conf.beat_schedule = {
    'generate-daily-products-report': {
        'task': 'product.tasks.generate_daily_products_report',
        'schedule': crontab(hour=8, minute=0),
    },
}
