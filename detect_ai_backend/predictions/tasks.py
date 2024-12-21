import asyncio

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

from detect_ai_backend.celery import app as celery_app
from detect_ai_backend.utils.celery import publish_message_to_group
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


def single_publish(connection_id, message):
    channel_layer = get_channel_layer()
    channel_layer.group_send(connection_id, message)


@shared_task(
    name=f"{settings.APP_NAME}.predict_result",
    retry_kwargs={"max_retries": 3, "countdown": 3},
)
def handle_predict_result(payload):
    email = payload.pop("email", "")
    image_url = payload.get("image_url", "")
    log_id = payload.pop("log_id", "")
    websockets = Websocket.objects.filter(user__email=email)
    connection_ids = [websocket.connection_id for websocket in websockets]
    message = {"type": "send_result", "message": payload}
    for connection_id in connection_ids:
        publish_message_to_group(message=message, group=connection_id)
    celery_app.send_task(
        f"{settings.APP_NAME}.post_predict_result",
        args=[email, image_url, log_id, payload],
    )
