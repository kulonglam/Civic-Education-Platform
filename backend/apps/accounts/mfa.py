"""TOTP multi-factor authentication for privileged accounts."""

from __future__ import annotations

import secrets

import pyotp
from django.conf import settings
from django.core.cache import cache

from apps.core.branding import PLATFORM_NAME

from apps.tenants.models import Membership

from .roles import is_platform_admin

MFA_PENDING_TTL = 300  # 5 minutes


def user_requires_mfa(user) -> bool:
    """Platform admins and organization owners/admins must use MFA when org requires it."""
    if not user or not user.is_authenticated:
        return False
    if is_platform_admin(user):
        return True
    privileged = Membership.objects.filter(
        user=user,
        role__in=(Membership.OWNER, Membership.ADMIN),
    ).select_related('organization')
    for membership in privileged:
        if membership.organization.force_mfa_for_admins:
            return True
    return False

def user_has_mfa_enabled(user) -> bool:
    profile = getattr(user, 'profile', None)
    return bool(profile and profile.mfa_enabled and profile.totp_secret)


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_for_secret(secret: str) -> pyotp.TOTP:
    return pyotp.TOTP(secret)


def verify_totp_code(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    totp = totp_for_secret(secret)
    return totp.verify(code, valid_window=1)


def provisioning_uri(user, secret: str) -> str:
    issuer = getattr(settings, 'MFA_ISSUER_NAME', PLATFORM_NAME)
    return totp_for_secret(secret).provisioning_uri(name=user.email, issuer_name=issuer)


def issue_mfa_challenge(user) -> str:
    token = secrets.token_urlsafe(32)
    cache.set(f'mfa:pending:{token}', str(user.pk), timeout=MFA_PENDING_TTL)
    return token


def consume_mfa_challenge(token: str):
    from django.contrib.auth import get_user_model

    if not token:
        return None
    user_id = cache.get(f'mfa:pending:{token}')
    if not user_id:
        return None
    cache.delete(f'mfa:pending:{token}')
    User = get_user_model()
    return User.objects.filter(pk=user_id).first()
