import asyncio

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.conf import settings

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
    websockets = Websocket.objects.filter(user__email=payload["email"])
    connection_ids = [websocket.connection_id for websocket in websockets]
    message = {**payload["results"]}
    for connection_id in connection_ids:
        publish_message_to_group(message=message, group=connection_id)
