"""WebSocket consumer for real-time in-app notifications.

Each authenticated user connects to their personal channel group
``notifications_<user_pk>``. The backend signals new notifications by
calling :func:`send_notification_to_user`, which pushes the payload to
all browser tabs belonging to that user simultaneously.
"""

import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

User = get_user_model()


def _group_name(user_pk) -> str:
    return f'notifications_{user_pk}'


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket endpoint: /ws/notifications/

    Authenticate via:
    - ``?token=<access_jwt>`` query param (simplest for browser clients), or
    - ``Authorization: Bearer <token>`` header (for programmatic clients).
    """

    async def connect(self):
        user = await self._authenticate()
        if user is None:
            await self.close(code=4001)
            return

        self.user = user
        self.group = _group_name(user.pk)
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if hasattr(self, 'group'):
            await self.channel_layer.group_discard(self.group, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Clients may send a ping to keep the connection alive
        if text_data:
            try:
                msg = json.loads(text_data)
                if msg.get('type') == 'ping':
                    await self.send(json.dumps({'type': 'pong'}))
            except (ValueError, KeyError):
                pass

    # ── Channel layer message handlers ──────────────────────────────────────

    async def notification_message(self, event):
        """Receive a notification event from the channel layer and forward
        it to the WebSocket client."""
        await self.send(json.dumps({
            'type': 'notification',
            'id': event.get('id'),
            'notification_type': event.get('notification_type'),
            'title': event.get('title'),
            'message': event.get('message'),
            'created_at': event.get('created_at'),
        }))

    # ── Authentication ───────────────────────────────────────────────────────

    async def _authenticate(self):
        token_str = self._extract_token()
        if not token_str:
            return None
        try:
            token = AccessToken(token_str)
            user_id = token['user_id']
            return await self._get_user(user_id)
        except (InvalidToken, TokenError, KeyError):
            return None

    def _extract_token(self) -> str | None:
        # Try ?token= query param first
        query = self.scope.get('query_string', b'').decode()
        for part in query.split('&'):
            if part.startswith('token='):
                return part[6:]
        # Fall back to Authorization header
        headers = dict(self.scope.get('headers', []))
        auth = headers.get(b'authorization', b'').decode()
        if auth.startswith('Bearer '):
            return auth[7:]
        # Check cookie
        cookie_header = headers.get(b'cookie', b'').decode()
        for crumb in cookie_header.split(';'):
            crumb = crumb.strip()
            if crumb.startswith('cep_access='):
                return crumb[len('cep_access='):]
        return None

    @database_sync_to_async
    def _get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


async def send_notification_to_user(channel_layer, user_pk, notification):
    """Push a notification dict to all WebSocket connections for ``user_pk``.

    Call this from Celery tasks or Django signals after creating a
    Notification row:

        from channels.layers import get_channel_layer
        from apps.notifications.consumers import send_notification_to_user

        await send_notification_to_user(get_channel_layer(), user.pk, {
            'id': str(notification.pk),
            'notification_type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'created_at': notification.created_at.isoformat(),
        })
    """
    await channel_layer.group_send(
        _group_name(user_pk),
        {
            'type': 'notification.message',
            **notification,
        },
    )
