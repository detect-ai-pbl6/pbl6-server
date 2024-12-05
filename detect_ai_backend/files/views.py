# Create your views here.
import asyncio

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, response, status, views

from detect_ai_backend.files.serializers import (
    SignedGCPStorageURLRequestSerializer,
    SignedGCPStorageURLResponseSerializer,
)
from detect_ai_backend.users.models import User
from detect_ai_backend.utils.gcp_storage import generate_upload_signed_url_v4
from detect_ai_backend.websocket.models import Websocket


class SignedGCPStorageURLView(generics.CreateAPIView):
    serializer_class = SignedGCPStorageURLRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: SignedGCPStorageURLResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        url, file_name = generate_upload_signed_url_v4(validated_data["mime_type"])

        return response.Response(
            status=status.HTTP_201_CREATED,
            data={
                "upload_url": url,
                "file_url": f"{settings.GCP_STORAGE_URL}/{file_name}",
            },
        )


class TestAPIView(views.APIView):

    @async_to_sync
    async def publish(self, connection_ids: list[str], message):
        channel_layer = get_channel_layer()
        return await asyncio.gather(
            *[
                channel_layer.group_send(connection_id, message)
                for connection_id in connection_ids
            ]
        )

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # validated_data = serializer.validated_data

        # url, file_name = generate_upload_signed_url_v4(validated_data["mime_type"])
        user = User.objects.get(id=2)
        websockets = Websocket.objects.filter(user=user)
        connection_ids = [websocket.connection_id for websocket in websockets]
        # async_to_sync(channel_layer.group_send)(
        #     websocket.connection_id, {"type": "chat_message", "message": "abc"}
        # )
        message = {"type": "chat_message", "message": "abc"}
        self.publish(connection_ids, message)
        return response.Response(status=status.HTTP_201_CREATED)
