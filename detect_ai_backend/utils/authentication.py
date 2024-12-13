import logging

from channels.auth import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.urls.exceptions import Resolver404
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from detect_ai_backend.users.models import User

logger = logging.getLogger(__name__)


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


class HandleRouteNotFoundMiddleware(BaseMiddleware):

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        try:
            inner_instance = await self.inner(scope, receive, send)
            return inner_instance
        except (Resolver404, ValueError) as e:
            if "No route found for path" not in str(e) and scope["type"] not in [
                "http",
                "websocket",
            ]:
                raise e
            elif scope["type"] == "websocket":
                return self.handle_ws_route_error

    async def handle_ws_route_error(self, receive, send):
        await send({"type": "websocket.close", "code": 4001})
