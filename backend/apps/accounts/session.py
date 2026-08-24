"""Server-side session controls: idle timeout and epoch-based revocation."""

from __future__ import annotations

import time

from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed

PRIVILEGED_PLATFORM_ROLES = frozenset({'admin', 'super_admin', 'editor', 'moderator'})
PRIVILEGED_ORG_ROLES = frozenset({'owner', 'admin'})

ACTIVITY_CACHE_KEY = 'session:activity:{user_id}'


def session_idle_seconds() -> int:
    return int(getattr(settings, 'SESSION_IDLE_TIMEOUT_SECONDS', 30 * 60))


def is_privileged_user(user) -> bool:
    """Privileged sessions enforce idle timeout (platform staff or org admins)."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    role = getattr(getattr(user, 'role', None), 'name', None)
    if role in PRIVILEGED_PLATFORM_ROLES:
        return True
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return True
    try:
        from apps.tenants.models import Membership

        return Membership.objects.filter(
            user=user,
            role__in=PRIVILEGED_ORG_ROLES,
        ).exists()
    except Exception:  # noqa: BLE001 — DB unavailable during early auth
        return False


def touch_session_activity(user_id) -> None:
    ttl = session_idle_seconds() * 2
    cache.set(ACTIVITY_CACHE_KEY.format(user_id=user_id), time.time(), timeout=max(ttl, 60))


def check_session_idle(user) -> None:
    """Raise AuthenticationFailed if a privileged user has been idle too long."""
    if not is_privileged_user(user):
        touch_session_activity(user.id)
        return

    key = ACTIVITY_CACHE_KEY.format(user_id=user.id)
    last = cache.get(key)
    now = time.time()
    idle_limit = session_idle_seconds()
    if last is not None and (now - float(last)) > idle_limit:
        raise AuthenticationFailed({
            'detail': 'Session expired due to inactivity.',
            'code': 'session_idle',
        })
    touch_session_activity(user.id)


def get_session_epoch(user) -> int:
    profile = getattr(user, 'profile', None)
    if profile is None:
        from apps.accounts.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(user=user)
    return int(profile.session_epoch)


def bump_session_epoch(user) -> int:
    """Invalidate all outstanding JWTs for this user by advancing session_epoch."""
    from apps.accounts.models import UserProfile

    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.session_epoch = int(profile.session_epoch) + 1
    profile.save(update_fields=['session_epoch'])
    cache.delete(ACTIVITY_CACHE_KEY.format(user_id=user.id))
    return profile.session_epoch


def verify_session_epoch(user, validated_token) -> None:
    token_sv = validated_token.get('sv')
    if token_sv is None:
        # Legacy tokens issued before epoch support — allow once, then require refresh.
        return
    current = get_session_epoch(user)
    if int(token_sv) != current:
        raise AuthenticationFailed({
            'detail': 'Session has been revoked. Please sign in again.',
            'code': 'session_revoked',
        })
