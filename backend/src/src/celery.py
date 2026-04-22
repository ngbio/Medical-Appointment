import os
from celery import Celery

# Thiết lập Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

app = Celery('medical_appointment')

# Sử dụng config từ settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto discover tasks từ tất cả apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

