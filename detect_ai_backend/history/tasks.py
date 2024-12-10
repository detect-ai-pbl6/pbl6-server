from celery import shared_task
from django.conf import settings


@shared_task(name=f"{settings.APP_NAME}.predict.result")
def handle_predict_result(**kwargs):
    return kwargs
