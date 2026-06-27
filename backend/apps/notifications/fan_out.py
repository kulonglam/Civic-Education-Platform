"""Unified notification fan-out.

Call :func:`notify_user` to deliver a notification through every channel
the user has opted into (in-app, WebSocket push, web-push, SMS).

Example (from a Celery task or signal)::

    from apps.notifications.fan_out import notify_user

    notify_user(
        user=user,
        notification_type='quiz_result',
        title='Quiz passed!',
        message='You scored 95 % on Introduction to Democracy.',
        organization=org,  # optional
    )
"""

from __future__ import annotations

import logging

from django.conf import settings

from .models import Notification, NotificationPreference

logger = logging.getLogger(__name__)


def notify_user(
    *,
    user,
    notification_type: str,
    title: str,
    message: str,
    organization=None,
) -> Notification | None:
    """Create an in-app Notification and fan-out to configured channels.

    Returns the created :class:`~apps.notifications.models.Notification` row,
    or ``None`` if in-app delivery is disabled.
    """
    prefs = _get_or_create_prefs(user)

    notification = None
    if prefs.in_app:
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            organization=organization,
        )
        # Broadcast to open WebSocket tabs
        _ws_push(user, notification)

    if prefs.wants_push(notification_type):
        _web_push(user, title, message)

    if prefs.wants_sms(notification_type):
        _sms_push(user, message, organization)

    return notification


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_or_create_prefs(user) -> NotificationPreference:
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    return prefs


def _ws_push(user, notification: Notification) -> None:
    """Fire-and-forget async send to the user's WebSocket group."""
    try:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer
        from .consumers import send_notification_to_user

        layer = get_channel_layer()
        if layer is None:
            return
        async_to_sync(send_notification_to_user)(
            layer,
            user.pk,
            {
                'id': str(notification.pk),
                'notification_type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'created_at': notification.created_at.isoformat(),
            },
        )
    except Exception as exc:  # channels not installed / Redis down
        logger.debug('WS push skipped: %s', exc)


def _web_push(user, title: str, message: str) -> None:
    try:
        from .push_services import send_push_to_user
        send_push_to_user(user=user, title=title, body=message)
    except Exception as exc:
        logger.debug('Web Push skipped: %s', exc)


def _sms_push(user, message: str, organization) -> None:
    try:
        from .sms_services import send_sms_to_user
        send_sms_to_user(user=user, message=message, organization=organization)
    except Exception as exc:
        logger.debug('SMS fan-out skipped: %s', exc)
