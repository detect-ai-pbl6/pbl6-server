import json
import uuid

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from detect_ai_backend.websocket.models import Websocket

User = get_user_model()


class WsConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope["user"]
        self.connection_id = uuid.uuid4().hex
        async_to_sync(self.channel_layer.group_add)(
            str(self.connection_id), self.channel_name
        )
        Websocket.objects.create(**{"connection_id": self.connection_id, "user": user})
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(
            self.channel_layer.group_discard(self.connection_id, self.channel_name)
        )
        Websocket.objects.filter(connection_id=self.connection_id).delete()

    def receive(self, text_data):
        pass

    def send_result(self, event):
        # Receive message from room group
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))

    def authenticate_user(self, token):
        try:
            # Validate the token
            validated_token = AccessToken(token)

            # Get the user ID from the token
            user_id = validated_token["user_id"]

            # Fetch the user
            user = User.objects.get(id=user_id)
            return user

        except (InvalidToken, TokenError, User.DoesNotExist):
            return None


class Handle404Consumer(WebsocketConsumer):
    def connect(self):
        self.close(code=404)
