"""OpenID Connect helpers for Enterprise SSO (per-org or global fallback)."""

from __future__ import annotations

import json
import logging
import secrets
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.core.safe_http import assert_http_url, safe_urlopen
from apps.tenants.models import Membership, Organization, OrganizationSsoConfig

logger = logging.getLogger(__name__)

User = get_user_model()
STATE_TTL = 600
METADATA_CACHE_TTL = 3600
JWKS_CACHE_TTL = 3600


@dataclass
class OidcCredentials:
    issuer: str
    client_id: str
    client_secret: str
    scopes: str
    source: str  # 'org' | 'global'


def redirect_uri() -> str:
    if settings.OIDC_REDIRECT_URI:
        return settings.OIDC_REDIRECT_URI
    base = settings.API_BASE_URL.rstrip('/')
    return f'{base}/api/auth/sso/callback/'


def global_oidc_configured() -> bool:
    return bool(settings.OIDC_ISSUER and settings.OIDC_CLIENT_ID and settings.OIDC_CLIENT_SECRET)


def get_org_sso_config(organization: Organization | None) -> OrganizationSsoConfig | None:
    if organization is None:
        return None
    return OrganizationSsoConfig.objects.filter(organization=organization).first()


def resolve_oidc_credentials(organization: Organization | None) -> OidcCredentials | None:
    """Prefer per-org SSO config; fall back to platform-wide OIDC env vars."""
    org_cfg = get_org_sso_config(organization)
    if org_cfg and org_cfg.is_ready:
        issuer = assert_http_url(org_cfg.issuer.rstrip('/'), allow_http=False)
        return OidcCredentials(
            issuer=issuer,
            client_id=org_cfg.client_id,
            client_secret=org_cfg.client_secret,
            scopes=org_cfg.scopes or 'openid email profile',
            source='org',
        )
    if global_oidc_configured():
        issuer = assert_http_url(settings.OIDC_ISSUER.rstrip('/'), allow_http=False)
        return OidcCredentials(
            issuer=issuer,
            client_id=settings.OIDC_CLIENT_ID,
            client_secret=settings.OIDC_CLIENT_SECRET,
            scopes=settings.OIDC_SCOPES,
            source='global',
        )
    return None


def oidc_configured(organization: Organization | None = None) -> bool:
    return resolve_oidc_credentials(organization) is not None


def _metadata_cache_key(issuer: str) -> str:
    return f'oidc:metadata:{issuer}'


def _jwks_cache_key(issuer: str) -> str:
    return f'oidc:jwks:{issuer}'


def fetch_oidc_metadata(creds: OidcCredentials) -> dict[str, Any]:
    key = _metadata_cache_key(creds.issuer)
    cached = cache.get(key)
    if cached:
        return cached
    url = f'{creds.issuer}/.well-known/openid-configuration'
    with safe_urlopen(url, timeout=10, allow_http=False) as response:
        metadata = json.loads(response.read().decode('utf-8'))
    cache.set(key, metadata, METADATA_CACHE_TTL)
    return metadata


def _fetch_jwks(creds: OidcCredentials, jwks_uri: str) -> dict[str, Any]:
    key = _jwks_cache_key(creds.issuer)
    cached = cache.get(key)
    if cached:
        return cached
    with safe_urlopen(jwks_uri, timeout=10, allow_http=False) as response:
        jwks = json.loads(response.read().decode('utf-8'))
    cache.set(key, jwks, JWKS_CACHE_TTL)
    return jwks


def store_sso_state(org_slug: str) -> tuple[str, str]:
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(24)
    cache.set(
        f'sso:state:{state}',
        {'org_slug': org_slug, 'nonce': nonce},
        STATE_TTL,
    )
    return state, nonce


def pop_sso_state(state: str) -> dict[str, Any] | None:
    key = f'sso:state:{state}'
    payload = cache.get(key)
    if payload is not None:
        cache.delete(key)
    return payload


def build_authorize_url(org_slug: str, organization: Organization) -> tuple[str, str]:
    creds = resolve_oidc_credentials(organization)
    if creds is None:
        raise ValueError('SSO is not configured for this organization.')
    metadata = fetch_oidc_metadata(creds)
    state, nonce = store_sso_state(org_slug)
    params = {
        'client_id': creds.client_id,
        'response_type': 'code',
        'scope': creds.scopes,
        'redirect_uri': redirect_uri(),
        'state': state,
        'nonce': nonce,
    }
    return f"{metadata['authorization_endpoint']}?{urllib.parse.urlencode(params)}", state


def exchange_code_for_tokens(code: str, organization: Organization) -> dict[str, Any]:
    creds = resolve_oidc_credentials(organization)
    if creds is None:
        raise ValueError('SSO is not configured for this organization.')
    metadata = fetch_oidc_metadata(creds)
    payload = urllib.parse.urlencode(
        {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri(),
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
        }
    ).encode('utf-8')
    request = urllib.request.Request(
        metadata['token_endpoint'],
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with safe_urlopen(request, timeout=15, allow_http=False) as response:
        return json.loads(response.read().decode('utf-8'))


def fetch_userinfo(access_token: str, creds: OidcCredentials) -> dict[str, Any]:
    metadata = fetch_oidc_metadata(creds)
    request = urllib.request.Request(
        metadata['userinfo_endpoint'],
        headers={'Authorization': f'Bearer {access_token}'},
    )
    with safe_urlopen(request, timeout=10, allow_http=False) as response:
        return json.loads(response.read().decode('utf-8'))


def _verify_id_token(
    id_token: str,
    metadata: dict[str, Any],
    creds: OidcCredentials,
    nonce: str | None,
) -> dict[str, Any]:
    jwks_uri = metadata.get('jwks_uri')
    if not jwks_uri:
        raise ValueError('IdP metadata is missing jwks_uri — cannot verify id_token.')

    _fetch_jwks(creds, jwks_uri)
    jwks_client = jwt.PyJWKClient(jwks_uri, cache_jwk_set=True, lifespan=3600)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    except jwt.exceptions.PyJWKClientError as exc:
        raise ValueError(f'Could not resolve signing key from JWKS: {exc}') from exc

    try:
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=['RS256', 'RS384', 'RS512', 'ES256', 'ES384', 'PS256'],
            audience=creds.client_id,
            issuer=creds.issuer,
            options={'verify_exp': True, 'verify_iat': True},
        )
    except jwt.ExpiredSignatureError as exc:
        raise ValueError('id_token has expired.') from exc
    except jwt.InvalidAudienceError as exc:
        raise ValueError('id_token audience does not match OIDC client_id.') from exc
    except jwt.InvalidIssuerError as exc:
        raise ValueError('id_token issuer does not match configured issuer.') from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError(f'id_token signature verification failed: {exc}') from exc

    if nonce is not None and claims.get('nonce') != nonce:
        raise ValueError('id_token nonce mismatch — possible replay attack.')

    return claims


def claims_from_tokens(
    token_payload: dict[str, Any],
    organization: Organization,
    nonce: str | None = None,
) -> dict[str, Any]:
    creds = resolve_oidc_credentials(organization)
    if creds is None:
        raise ValueError('SSO is not configured for this organization.')

    id_token = token_payload.get('id_token')
    if id_token:
        metadata = fetch_oidc_metadata(creds)
        return _verify_id_token(id_token, metadata, creds, nonce)

    access_token = token_payload.get('access_token')
    if access_token:
        return fetch_userinfo(access_token, creds)

    return {}


def get_or_create_user_from_sso(claims: dict[str, Any], org_slug: str | None):
    from apps.accounts.models import Role

    email = (claims.get('email') or '').strip().lower()
    if not email:
        raise ValueError('Identity provider did not return an email address.')

    first_name = claims.get('given_name') or claims.get('name', '').split(' ')[0] or 'SSO'
    last_name = claims.get('family_name') or 'User'
    if claims.get('name') and not claims.get('given_name'):
        parts = claims['name'].split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else last_name

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': first_name[:150],
            'last_name': last_name[:150],
            'role': Role.objects.get_or_create(name='citizen')[0],
            'email_verified': True,
            'is_active': True,
        },
    )
    if not created and not user.is_active:
        raise ValueError('Account is inactive.')

    if org_slug:
        organization = Organization.objects.filter(slug=org_slug, is_active=True).first()
        if organization:
            Membership.objects.get_or_create(
                organization=organization,
                user=user,
                defaults={'role': Membership.MEMBER},
            )

    return user


def issue_jwt_tokens(user):
    from apps.accounts.tokens import EmailTokenObtainPairSerializer

    refresh = EmailTokenObtainPairSerializer.get_token(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def frontend_callback_url(tokens: dict[str, str], org_slug: str | None = None) -> str:
    params: dict[str, str] = {
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    }
    if org_slug:
        params['org'] = org_slug
    fragment = urllib.parse.urlencode(params)
    return f'{settings.FRONTEND_URL.rstrip("/")}/sso/callback#{fragment}'
