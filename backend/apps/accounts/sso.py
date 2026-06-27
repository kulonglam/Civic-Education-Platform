"""OpenID Connect helpers for Enterprise SSO."""

from __future__ import annotations

import json
import logging
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from apps.tenants.models import Membership

logger = logging.getLogger(__name__)

User = get_user_model()
STATE_TTL = 600
METADATA_CACHE_KEY = 'oidc:metadata'
METADATA_CACHE_TTL = 3600
JWKS_CACHE_KEY = 'oidc:jwks'
JWKS_CACHE_TTL = 3600


def oidc_configured() -> bool:
    return bool(settings.OIDC_ISSUER and settings.OIDC_CLIENT_ID and settings.OIDC_CLIENT_SECRET)


def redirect_uri() -> str:
    if settings.OIDC_REDIRECT_URI:
        return settings.OIDC_REDIRECT_URI
    base = settings.API_BASE_URL.rstrip('/')
    return f'{base}/api/auth/sso/callback/'


def fetch_oidc_metadata() -> dict[str, Any]:
    cached = cache.get(METADATA_CACHE_KEY)
    if cached:
        return cached
    issuer = settings.OIDC_ISSUER.rstrip('/')
    url = f'{issuer}/.well-known/openid-configuration'
    with urllib.request.urlopen(url, timeout=10) as response:
        metadata = json.loads(response.read().decode('utf-8'))
    cache.set(METADATA_CACHE_KEY, metadata, METADATA_CACHE_TTL)
    return metadata


def _fetch_jwks(jwks_uri: str) -> dict[str, Any]:
    """Fetch and cache the IdP's public JWKS for signature verification."""
    cached = cache.get(JWKS_CACHE_KEY)
    if cached:
        return cached
    with urllib.request.urlopen(jwks_uri, timeout=10) as response:
        jwks = json.loads(response.read().decode('utf-8'))
    cache.set(JWKS_CACHE_KEY, jwks, JWKS_CACHE_TTL)
    return jwks


def store_sso_state(org_slug: str) -> tuple[str, str]:
    """
    Create a CSRF state token and a nonce.
    Returns (state, nonce); both are stored in cache and the nonce
    must be forwarded to the IdP and later verified in the id_token.
    """
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


def build_authorize_url(org_slug: str) -> tuple[str, str]:
    """
    Build the IdP authorization URL.
    Returns (url, state) so the caller can store the state for CSRF verification.
    The nonce is embedded in the state payload and sent to the IdP so it can
    be validated when the id_token is returned.
    """
    metadata = fetch_oidc_metadata()
    state, nonce = store_sso_state(org_slug)
    params = {
        'client_id': settings.OIDC_CLIENT_ID,
        'response_type': 'code',
        'scope': settings.OIDC_SCOPES,
        'redirect_uri': redirect_uri(),
        'state': state,
        'nonce': nonce,
    }
    return f"{metadata['authorization_endpoint']}?{urllib.parse.urlencode(params)}", state


def exchange_code_for_tokens(code: str) -> dict[str, Any]:
    metadata = fetch_oidc_metadata()
    payload = urllib.parse.urlencode(
        {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri(),
            'client_id': settings.OIDC_CLIENT_ID,
            'client_secret': settings.OIDC_CLIENT_SECRET,
        }
    ).encode('utf-8')
    request = urllib.request.Request(
        metadata['token_endpoint'],
        data=payload,
        method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode('utf-8'))


def fetch_userinfo(access_token: str) -> dict[str, Any]:
    metadata = fetch_oidc_metadata()
    request = urllib.request.Request(
        metadata['userinfo_endpoint'],
        headers={'Authorization': f'Bearer {access_token}'},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))


def _verify_id_token(id_token: str, metadata: dict[str, Any], nonce: str | None) -> dict[str, Any]:
    """
    Cryptographically verify an OIDC id_token using the IdP's published JWKS.

    Validates:
    - Signature (via JWKS)
    - Issuer (`iss`)
    - Audience (`aud`)
    - Expiry (`exp`)
    - Nonce (replay protection)
    """
    jwks_uri = metadata.get('jwks_uri')
    if not jwks_uri:
        raise ValueError('IdP metadata is missing jwks_uri — cannot verify id_token.')

    jwks_data = _fetch_jwks(jwks_uri)

    # PyJWT 2.x: use PyJWKClient to select the right key from the JWKS
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
            audience=settings.OIDC_CLIENT_ID,
            issuer=settings.OIDC_ISSUER.rstrip('/'),
            options={'verify_exp': True, 'verify_iat': True},
        )
    except jwt.ExpiredSignatureError as exc:
        raise ValueError('id_token has expired.') from exc
    except jwt.InvalidAudienceError as exc:
        raise ValueError('id_token audience does not match OIDC_CLIENT_ID.') from exc
    except jwt.InvalidIssuerError as exc:
        raise ValueError('id_token issuer does not match OIDC_ISSUER.') from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError(f'id_token signature verification failed: {exc}') from exc

    # Nonce check — prevents replay attacks
    if nonce is not None and claims.get('nonce') != nonce:
        raise ValueError('id_token nonce mismatch — possible replay attack.')

    return claims


def claims_from_tokens(
    token_payload: dict[str, Any],
    nonce: str | None = None,
) -> dict[str, Any]:
    """
    Extract and cryptographically verify claims from the token endpoint response.

    Prefers the id_token (JWKS-verified) over the userinfo endpoint.
    Falls back to userinfo only when no id_token is present.
    """
    id_token = token_payload.get('id_token')
    if id_token:
        try:
            metadata = fetch_oidc_metadata()
            return _verify_id_token(id_token, metadata, nonce)
        except ValueError:
            raise  # propagate security errors — do not silently fall through
        except Exception as exc:
            logger.exception('Unexpected error verifying id_token; falling back to userinfo')
            # Only fall back on unexpected infrastructure errors, not on validation failures
            pass

    access_token = token_payload.get('access_token')
    if access_token:
        return fetch_userinfo(access_token)

    return {}


def get_or_create_user_from_sso(claims: dict[str, Any], org_slug: str | None):
    from apps.accounts.models import Role
    from apps.tenants.models import Organization

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
    from rest_framework_simplejwt.tokens import RefreshToken

    from apps.tenants.services import get_user_organization

    refresh = RefreshToken.for_user(user)
    refresh['email'] = user.email
    refresh['role'] = user.role.name
    organization = get_user_organization(user)
    if organization is not None:
        refresh['org'] = str(organization.id)
        refresh['org_slug'] = organization.slug
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def frontend_callback_url(tokens: dict[str, str], org_slug: str | None = None) -> str:
    """
    Redirect to the frontend SPA callback page, passing tokens in the URL
    *fragment* (hash) rather than query parameters.

    Hash fragments are never sent to servers (no Referer leakage, no server
    access-log exposure) and are not stored in browser history on the server side.
    """
    params: dict[str, str] = {
        'access': tokens['access'],
        'refresh': tokens['refresh'],
    }
    if org_slug:
        params['org'] = org_slug
    fragment = urllib.parse.urlencode(params)
    return f'{settings.FRONTEND_URL.rstrip("/")}/sso/callback#{fragment}'
