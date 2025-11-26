# myproject/celery.py
import os
from celery import Celery

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'siraj.settings')

# Create Celery application instance
app = Celery('siraj')

# Configure Celery using Django settings
# namespace='CELERY' means all Celery configs should start with CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
# Looks for tasks.py in each installed app
app.autodiscover_tasks()

# Optional: Basic task for testing
@app.task(bind=True , ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# os.environ.setdefault(): Ensures Celery uses your Django settings

# Celery('Siraj'): Creates a Celery application named 'Siraj'

# config_from_object(): Loads configuration from Django settings

# autodiscover_tasks(): Automatically finds tasks.py files in your apps

# @app.task(bind=True): Creates a task that can access itself (via self)