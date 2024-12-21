import logging

from django.conf import settings
from django.utils import timezone

from detect_ai_backend.api_keys.models import APIKeyLog
from detect_ai_backend.celery import app as celery_app
from detect_ai_backend.history.models import History
from detect_ai_backend.users.models import User

logger = logging.getLogger(__name__)


@celery_app.task(
    name=f"{settings.APP_NAME}.post_predict_result",
    retry_kwargs={"max_retries": 3, "countdown": 3},
)
def post_predict_resutl(email, image_url, log_id, payload):
    try:
        user = User.objects.get(email=email)
        history = History(user=user, results=payload, image_url=image_url)
        history.save()
    except User.DoesNotExist:
        logger.info(f"user {email} does not exist")
    try:
        api_key_log = APIKeyLog.objects.get(id=log_id)
        api_key = api_key_log.api_key
        api_key.total_usage += 1
        api_key.last_used = timezone.now()
        api_key.save()
        api_key_log.status = payload["status"]
        api_key_log.save()
    except APIKeyLog.DoesNotExist:
        logger.info(f"log id: {log_id} does not exist")
