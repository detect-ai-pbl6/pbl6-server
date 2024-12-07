from channels.auth import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from detect_ai_backend.users.models import User


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class AuthMiddleware(BaseMiddleware):
    """
    Custom middleware for WebSocket authentication using JWT
    """

    def __init__(self, app):
        # Store the ASGI application
        self.app = app

    async def __call__(self, scope, receive, send):
        # Parse headers
        headers = dict(scope.get("headers", []))

        # Look for authentication token
        token = headers.get(b"authentication", b"").decode("utf-8")
        if not token:
            await send({"type": "websocket.close", "code": 4001})
            return
        # Authenticate user
        user = await self.authenticate_user(token)

        if not user or not user.id:
            # Close connection if authentication fails
            await send({"type": "websocket.close", "code": 4001})
            return

        # Add authenticated user to scope
        scope["user"] = user

        # Continue with the application
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def authenticate_user(self, token):
        """
        Authenticate user using JWT token
        """
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


def AuthMiddlewareStack(inner):
    return AuthMiddleware(inner)
