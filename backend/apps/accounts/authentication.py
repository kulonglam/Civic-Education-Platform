"""Cookie-aware JWT authentication.

Checks httpOnly cookies first (preferred, more secure), then falls back to
the standard Authorization header so CLI clients and the OpenAPI docs keep
working without friction.

Also enforces enterprise session controls: session epoch (revocation) and
server-side idle timeout for privileged roles.
"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .session import check_session_idle, verify_session_epoch


ACCESS_COOKIE = getattr(settings, 'JWT_ACCESS_COOKIE', 'cep_access')
REFRESH_COOKIE = getattr(settings, 'JWT_REFRESH_COOKIE', 'cep_refresh')


class JWTCookieAuthentication(JWTAuthentication):
    """Authenticate via httpOnly cookie if present; fall back to Bearer header."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if raw_token:
            try:
                validated = self.get_validated_token(raw_token.encode())
                user = self.get_user(validated)
                self._enforce_session_controls(user, validated)
                return user, validated
            except (InvalidToken, TokenError):
                # Cookie is invalid/expired — fall through to header
                pass
        result = super().authenticate(request)
        if result is None:
            return None
        user, validated = result
        self._enforce_session_controls(user, validated)
        return user, validated

    @staticmethod
    def _enforce_session_controls(user, validated):
        verify_session_epoch(user, validated)
        check_session_idle(user)
