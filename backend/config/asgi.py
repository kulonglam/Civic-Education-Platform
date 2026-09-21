"""ASGI config for CivicHub.

Handles both HTTP and WebSocket connections via Django Channels / Daphne.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

django_asgi_app = get_asgi_application()

from apps.core.websocket import allowed_websocket_origins  # noqa: E402
from apps.notifications.consumers import NotificationConsumer  # noqa: E402

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]

_inner = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
_origins = allowed_websocket_origins()
_websocket = OriginValidator(_inner, _origins) if _origins else AllowedHostsOriginValidator(_inner)

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': _websocket,
})
