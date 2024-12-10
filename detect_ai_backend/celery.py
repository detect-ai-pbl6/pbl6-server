import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "detect_ai_backend.settings.local")

app = Celery(settings.CELERY_APP_NAME)

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
app.conf.result_backend = "rpc://"
app.conf.task_default_queue = f"{settings.CELERY_APP_NAME}_queue"
