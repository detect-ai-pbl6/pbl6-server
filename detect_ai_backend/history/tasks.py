from django.conf import settings
from django.utils import timezone

from detect_ai_backend.api_keys.models import APIKeyLog
from detect_ai_backend.celery import app as celery_app
from detect_ai_backend.history.models import History
from detect_ai_backend.users.models import User


@celery_app.task(name=f"{settings.APP_NAME}.post_predict_result")
def post_predict_resutl(email, image_url, log_id, payload):
    user = User.objects.get(email=email)
    history = History(user=user, results=payload, image_url=image_url)
    history.save()
    api_key_log = APIKeyLog.objects.get(id=log_id)
    api_key = api_key_log.api_key
    api_key.total_usage += 1
    api_key.last_used = timezone.now()
    api_key.save()
    api_key_log.status = payload["status"]
    api_key_log.save()
