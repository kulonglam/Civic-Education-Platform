"""ASGI config for Civic Education RSS.

Handles both HTTP (via Django WSGI-over-ASGI shim) and WebSocket
connections (via Django Channels / Daphne).
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from django.urls import path

# Prefer an explicit DJANGO_SETTINGS_MODULE from the host (Render dashboard /
# Dockerfile). Fall back to development only for local runs.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Load Django before importing consumers to ensure apps are ready.
django_asgi_app = get_asgi_application()

from apps.notifications.consumers import NotificationConsumer  # noqa: E402

websocket_urlpatterns = [
    path('ws/notifications/', NotificationConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
