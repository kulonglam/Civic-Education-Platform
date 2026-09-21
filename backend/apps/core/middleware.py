"""Custom middleware for CivicHub."""

from django.conf import settings
from django.http import JsonResponse


class SecurityHeadersMiddleware:
    """Extra browser hardening headers used for enterprise security reviews."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault(
            'Permissions-Policy',
            'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
        )
        response.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        response.setdefault('X-Content-Type-Options', 'nosniff')
        return response


class ContentSecurityPolicyMiddleware:
    """Emit a Content-Security-Policy response header based on settings.

    Enable by adding 'apps.core.middleware.ContentSecurityPolicyMiddleware'
    to MIDDLEWARE (after SecurityMiddleware is fine).
    """

    _DIRECTIVE_MAP = {
        'CSP_DEFAULT_SRC': 'default-src',
        'CSP_SCRIPT_SRC': 'script-src',
        'CSP_STYLE_SRC': 'style-src',
        'CSP_FONT_SRC': 'font-src',
        'CSP_IMG_SRC': 'img-src',
        'CSP_CONNECT_SRC': 'connect-src',
        'CSP_FRAME_ANCESTORS': 'frame-ancestors',
        'CSP_MEDIA_SRC': 'media-src',
        'CSP_OBJECT_SRC': 'object-src',
        'CSP_WORKER_SRC': 'worker-src',
        'CSP_MANIFEST_SRC': 'manifest-src',
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self._header_value = self._build_header()

    def _build_header(self) -> str:
        parts = []
        for setting_name, directive in self._DIRECTIVE_MAP.items():
            sources = getattr(settings, setting_name, None)
            if sources:
                parts.append(f"{directive} {' '.join(sources)}")
        if getattr(settings, 'CSP_UPGRADE_INSECURE_REQUESTS', False):
            parts.append('upgrade-insecure-requests')
        return '; '.join(parts)

    def __call__(self, request):
        response = self.get_response(request)
        if self._header_value:
            response['Content-Security-Policy'] = self._header_value
        return response


class IpAllowlistMiddleware:
    """Enforce organization IP allowlist when configured (non-empty)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from apps.core.db import client_ip_from_request, ip_allowed
        from apps.tenants.context import get_current_organization

        organization = get_current_organization()
        allowlist = getattr(organization, 'ip_allowlist', None) if organization else None
        if allowlist:
            client_ip = client_ip_from_request(request)
            if not ip_allowed(client_ip, allowlist):
                return JsonResponse(
                    {
                        'detail': 'Access denied from this network address.',
                        'code': 'ip_not_allowed',
                    },
                    status=403,
                )
        return self.get_response(request)


class SetJWTCookieMiddleware:
    """Intercept JSON responses that carry access/refresh tokens and mirror them
    into httpOnly cookies so the browser never needs to touch localStorage.

    Views still return tokens in the body (for backward-compat with API clients);
    this middleware adds the cookies as a bonus so browser clients gain XSS
    protection transparently.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return self._maybe_set_cookies(request, response)

    def _maybe_set_cookies(self, request, response):
        import json

        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response
        if response.status_code not in (200, 201):
            return response

        try:
            body = json.loads(response.content)
        except (ValueError, AttributeError):
            return response

        if not isinstance(body, dict):
            return response

        access = body.get('access')
        refresh = body.get('refresh')
        if not (access or refresh):
            return response

        secure = getattr(settings, 'JWT_COOKIE_SECURE', not settings.DEBUG)
        samesite = getattr(settings, 'JWT_COOKIE_SAMESITE', 'Lax')
        access_max_age = int(
            settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME').total_seconds()
        )
        refresh_max_age = int(
            settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').total_seconds()
        )

        if access:
            response.set_cookie(
                settings.JWT_ACCESS_COOKIE,
                access,
                max_age=access_max_age,
                httponly=True,
                secure=secure,
                samesite=samesite,
                path='/',
            )
        if refresh:
            response.set_cookie(
                settings.JWT_REFRESH_COOKIE,
                refresh,
                max_age=refresh_max_age,
                httponly=True,
                secure=secure,
                samesite=samesite,
                path='/api/',
            )
        return response
