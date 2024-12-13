import asyncio

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, response, status

from detect_ai_backend.api_keys.models import APIKeyLog, APIKeyLogStatus
from detect_ai_backend.celery import app as celery_app
from detect_ai_backend.predictions.serializers import PredictionsSerializer
from detect_ai_backend.utils.permissions import HasAPIKey
from detect_ai_backend.utils.swagger import get_api_key_header


class PredictionCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, HasAPIKey]
    serializer_class = PredictionsSerializer

    @swagger_auto_schema(manual_parameters=[get_api_key_header()])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        api_key_log = APIKeyLog.objects.create(
            api_key=self.request.api_key, status=APIKeyLogStatus.PENDING
        )
        payload = {
            "email": request.user.email,
            "image_url": validated_data["image_url"],
            "log_id": api_key_log.id,
        }
        celery_app.send_task(
            f"{settings.AI_SERVER_NAME}.predict",
            args=(payload,),
            queue=f"{settings.AI_SERVER_NAME}_queue",
        )

        return response.Response(status=status.HTTP_201_CREATED)

    @async_to_sync
    async def publish(self, connection_ids: list[str], message):
        channel_layer = get_channel_layer()
        return await asyncio.gather(
            *[
                channel_layer.group_send(connection_id, message)
                for connection_id in connection_ids
            ]
        )
