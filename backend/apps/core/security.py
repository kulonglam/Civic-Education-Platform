"""Structured security event logging for monitoring and incident response."""

from __future__ import annotations

import logging
from typing import Any

security_logger = logging.getLogger('security')


def _client_ip(request) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_security_event(
    event_type: str,
    *,
    request=None,
    user=None,
    detail: dict[str, Any] | None = None,
) -> None:
    """Emit a single-line structured security log entry."""
    payload = {
        'event': event_type,
        'ip': _client_ip(request),
        'user_id': str(user.pk) if user and getattr(user, 'pk', None) else None,
        'user_email': getattr(user, 'email', None) if user else None,
        'path': getattr(request, 'path', None) if request else None,
        'method': getattr(request, 'method', None) if request else None,
        **(detail or {}),
    }
    # Filter None values for cleaner log lines
    payload = {k: v for k, v in payload.items() if v is not None}
    security_logger.warning('security_event %s', payload)
