"""
ASGI config for detect_ai_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

asgi_application = get_asgi_application()  # noqa

from django.urls import re_path  # noqa

from detect_ai_backend.utils.authentication import AuthMiddlewareStack  # noqa
from detect_ai_backend.websocket import consumers  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "detect_ai_backend.settings.production")

websocket_urlpatterns = [
    re_path(r"ws/test", consumers.WsConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": asgi_application,
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
