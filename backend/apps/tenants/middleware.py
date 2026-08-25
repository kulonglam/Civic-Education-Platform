"""Resolves the current tenant for each request.

Resolution order:
    1. ``X-Tenant-Slug`` header for anonymous/public requests.
    2. For Bearer tokens, ``X-Tenant-Slug`` is honored only when the token's
       user is a member of that organization (org switcher); otherwise the JWT
       ``org`` claim is used so a header cannot spoof another tenant.
    3. ``org`` claim from the JWT when no valid header is supplied.

The resolved organization is stored in the tenant context for the duration of
the request and cleared afterwards.
"""

import logging

from django.db.utils import DatabaseError, OperationalError

from .context import (
    clear_current_organization,
    reset_tenant_fail_closed,
    set_current_organization,
    set_tenant_fail_closed,
)
from .models import Membership, Organization
from .rls import apply_rls_session

logger = logging.getLogger(__name__)

# Liveness/readiness must not depend on tenant DB lookups (or fail when
# migrations have not run yet). Frontend and browsers may still send a slug.
_SKIP_TENANT_PREFIXES = (
    '/api/health/',
    '/api/v1/health/',
    '/api/ready/',
    '/api/v1/ready/',
)

_FAIL_CLOSED_PREFIXES = ('/api/',)
_FAIL_CLOSED_EXEMPT = (
    '/api/health/',
    '/api/v1/health/',
    '/api/ready/',
    '/api/v1/ready/',
    '/api/docs/',
    '/api/schema/',
    '/api/redoc/',
    '/api/branding/',
    '/api/v1/branding/',
)


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        fail_token = None
        if self._should_fail_closed(request):
            fail_token = set_tenant_fail_closed(True)
        organization = self._resolve(request)
        org_token = set_current_organization(organization)
        apply_rls_session(organization)
        try:
            return self.get_response(request)
        finally:
            apply_rls_session(None)
            clear_current_organization(org_token)
            if fail_token is not None:
                reset_tenant_fail_closed(fail_token)

    @staticmethod
    def _should_fail_closed(request) -> bool:
        path = request.path if request.path.endswith('/') else f'{request.path}/'
        if any(path.startswith(prefix) for prefix in _FAIL_CLOSED_EXEMPT):
            return False
        return any(path.startswith(prefix) for prefix in _FAIL_CLOSED_PREFIXES)

    def _resolve(self, request):
        path = request.path if request.path.endswith('/') else f'{request.path}/'
        if path in _SKIP_TENANT_PREFIXES or any(
            path.startswith(prefix) for prefix in _SKIP_TENANT_PREFIXES
        ):
            return None

        try:
            return self._resolve_organization(request)
        except (OperationalError, DatabaseError) as exc:
            # Missing tables / bad DATABASE_URL should not turn every probe into 500.
            logger.exception('Tenant resolution failed (database): %s', exc)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.exception('Tenant resolution failed: %s', exc)
            return None

    def _resolve_organization(self, request):
        slug = request.headers.get('X-Tenant-Slug')
        auth = request.headers.get('Authorization', '')

        jwt_ctx = None
        if auth.startswith('Bearer '):
            jwt_ctx = self._jwt_context(auth.split(' ', 1)[1].strip())

        jwt_org = None
        if jwt_ctx and jwt_ctx.get('org_id'):
            jwt_org = Organization.objects.filter(id=jwt_ctx['org_id'], is_active=True).first()

        if slug:
            header_org = Organization.objects.filter(slug=slug, is_active=True).first()
            if header_org is None:
                return jwt_org

            if jwt_ctx and jwt_ctx.get('user_id'):
                if Membership.objects.filter(
                    organization=header_org,
                    user_id=jwt_ctx['user_id'],
                ).exists():
                    return header_org
                return jwt_org

            return header_org

        return jwt_org

    @staticmethod
    def _jwt_context(raw_token):
        try:
            from rest_framework_simplejwt.tokens import AccessToken

            token = AccessToken(raw_token)
            return {
                'user_id': token.get('user_id'),
                'org_id': token.get('org'),
            }
        except Exception:  # noqa: BLE001 - invalid/expired token -> no tenant
            return None
