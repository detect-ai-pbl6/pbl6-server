"""
WSGI config for detect_ai_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.wsgi import get_wsgi_application
from django.urls import re_path

from detect_ai_backend.websocket import consumers

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "detect_ai_backend.settings.production")

# application = get_wsgi_application()

websocket_urlpatterns = [
    re_path(r"ws/test", consumers.WsConsumer.as_asgi()),
]

application = ProtocolTypeRouter(
    {
        "http": get_wsgi_application(),
        # Just HTTP for now. (We can add other protocols later.)
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
