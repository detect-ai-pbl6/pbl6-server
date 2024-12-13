import asyncio

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

from detect_ai_backend.api_keys.models import APIKeyLog
from detect_ai_backend.history.models import History
from detect_ai_backend.users.models import User
from detect_ai_backend.utils.celery_utils import publish_message_to_group
from detect_ai_backend.websocket.models import Websocket


@async_to_sync
async def publish(connection_ids: list[str], message):
    channel_layer = get_channel_layer()
    return await asyncio.gather(
        *[
            channel_layer.group_send(connection_id, message)
            for connection_id in connection_ids
        ]
    )


@shared_task(name=f"{settings.APP_NAME}.predict_result")
def handle_predict_result(payload):
    email = payload.pop("email", "")
    image_url = payload.get("image_url", "")
    log_id = payload.pop("log_id", "")
    websockets = Websocket.objects.filter(user__email=email)
    connection_ids = [websocket.connection_id for websocket in websockets]
    message = {"type": "send_result", "message": payload}
    for connection_id in connection_ids:
        publish_message_to_group(message=message, group=connection_id)
    user = User.objects.get(email=email)
    history = History(user=user, results=payload, image_url=image_url)
    history.save()
    api_key_log = APIKeyLog.objects.get(id=log_id)
    api_key = api_key_log.api_key
    api_key.total_usage = api_key.total_usage + 1
    api_key.save()
    api_key_log.status = payload["status"]
    api_key_log.save()
