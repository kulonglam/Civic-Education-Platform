from decouple import config
from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured
import dj_database_url
import os

from apps.core.host_utils import (
    unique_hosts,
    render_hostname,
    redis_url_points_to_localhost,
    production_public_origin,
)

from .base import *  # noqa: F403

DEBUG = False

# Do not inherit base.py's localhost Celery / DB defaults in production.
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='')  # noqa: F405
REDIS_URL = config('REDIS_URL', default='')  # noqa: F405
_DATABASE_URL = config('DATABASE_URL', default='')
if not _DATABASE_URL:
    raise ImproperlyConfigured(
        'DATABASE_URL is required in production. '
        'On Render: Postgres → Info → copy Internal Database URL → set DATABASE_URL on the API service.'
    )
if redis_url_points_to_localhost(_DATABASE_URL):
    raise ImproperlyConfigured(
        'DATABASE_URL points to localhost. Set the Render Postgres Internal Database URL '
        '(not postgres://...@localhost:5432).'
    )
DATABASES = {  # noqa: F405
    'default': dj_database_url.config(
        default=_DATABASE_URL,
        conn_max_age=600,
    )
}

# ALLOWED_HOSTS is set in the dashboard for custom domains. Render also injects
# RENDER_EXTERNAL_HOSTNAME (e.g. civic-education-platform-66rb.onrender.com).
ALLOWED_HOSTS = unique_hosts(
    config('ALLOWED_HOSTS', default=''),
    render_hostname(),
)
# Workers and cron jobs on Render have no RENDER_EXTERNAL_HOSTNAME.
if not ALLOWED_HOSTS and os.environ.get('RENDER'):
    ALLOWED_HOSTS = ['.onrender.com']

CORS_ALLOWED_ORIGINS = [
    origin
    for origin in (
        production_public_origin(part)
        for part in config('CORS_ALLOWED_ORIGINS', default='').split(',')
    )
    if origin
]
_frontend = production_public_origin(FRONTEND_URL)  # noqa: F405
if not _frontend:
    raise ImproperlyConfigured(
        'FRONTEND_URL must be your public SPA HTTPS URL. A custom domain is not required — '
        'use the Render static site, e.g. https://civic-education-web-xxxx.onrender.com'
    )
if _frontend not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(_frontend)

# SSO / email links: prefer explicit API_BASE_URL, else this Render service URL.
_render_url = (os.environ.get('RENDER_EXTERNAL_URL') or '').strip().rstrip('/')
if _render_url and (
    not API_BASE_URL or API_BASE_URL.rstrip('/') in ('http://127.0.0.1:8000', 'http://localhost:8000')  # noqa: F405
):
    API_BASE_URL = _render_url  # noqa: F405

# Trust HTTPS origins for Django CSRF (admin, session cookie flows).
CSRF_TRUSTED_ORIGINS = unique_hosts(
    config('CSRF_TRUSTED_ORIGINS', default=''),
    *[f'https://{host}' for host in ALLOWED_HOSTS if host and not host.startswith('.')],
    _frontend,
)

CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept-language',
    'x-tenant-slug',
]

# Prefer JSON over DRF browsable HTML in production so browser Accept: text/html
# on /api/health/ does not pull missing static CSS from WhiteNoise.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,  # noqa: F405
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
X_FRAME_OPTIONS = 'DENY'
# JWT cookies must be Secure in production (overrides base default).
JWT_COOKIE_SECURE = True  # noqa: F405

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@civic-education.ss')
# Render free web services block SMTP 25/465/587. Prefer Brevo HTTPS when keyed.
if BREVO_API_KEY:  # noqa: F405
    EMAIL_BACKEND = 'apps.core.brevo_mail.BrevoAPIEmailBackend'

CELERY_TASK_ALWAYS_EAGER = False

# Prefer dedicated REDIS_URL; fall back to the Celery broker for cache/channels.
if not REDIS_URL and CELERY_BROKER_URL:  # noqa: F405
    REDIS_URL = CELERY_BROKER_URL  # noqa: F405
if REDIS_URL:  # noqa: F405
    CACHES = {  # noqa: F405
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }
    CHANNEL_LAYERS = {  # noqa: F405
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [REDIS_URL]},
        }
    }

# Fail fast on boot when critical production settings are missing.
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'ALLOWED_HOSTS must be set in production '
        '(or rely on RENDER_EXTERNAL_HOSTNAME on Render).'
    )
if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured(
        'Set FRONTEND_URL to your Render static site HTTPS URL '
        '(e.g. https://civic-education-web-xxxx.onrender.com), '
        'or set CORS_ALLOWED_ORIGINS to the same value.'
    )
if SECRET_KEY.startswith('django-insecure') or SECRET_KEY.startswith('change-me'):  # noqa: F405
    raise ImproperlyConfigured('SECRET_KEY must be a secure random value in production.')
ALLOW_DUMMY_BILLING_IN_PRODUCTION = config('ALLOW_DUMMY_BILLING_IN_PRODUCTION', default=False, cast=bool)  # noqa: F405
if BILLING_PROVIDER == 'dummy' and not ALLOW_DUMMY_BILLING_IN_PRODUCTION:  # noqa: F405
    raise ImproperlyConfigured(
        'BILLING_PROVIDER must be "stripe" in production, or set '
        'ALLOW_DUMMY_BILLING_IN_PRODUCTION=True when payments are not used '
        '(e.g. civic deployments in countries without Stripe).'
    )
if not CELERY_BROKER_URL:  # noqa: F405
    raise ImproperlyConfigured(
        'CELERY_BROKER_URL is required in production. '
        'On Render, link your Redis service Internal URL.'
    )
if redis_url_points_to_localhost(CELERY_BROKER_URL):  # noqa: F405
    raise ImproperlyConfigured(
        'CELERY_BROKER_URL points to localhost. Set Render Redis Internal URL '
        'on the API and worker services (not redis://localhost:6379).'
    )
if REDIS_URL and redis_url_points_to_localhost(REDIS_URL):  # noqa: F405
    raise ImproperlyConfigured(
        'REDIS_URL points to localhost. Set Render Redis Internal URL on the API and worker.'
    )
if BILLING_PROVIDER == 'stripe':  # noqa: F405
    if not STRIPE_SECRET_KEY:  # noqa: F405
        raise ImproperlyConfigured('STRIPE_SECRET_KEY is required when BILLING_PROVIDER=stripe.')
    if not STRIPE_WEBHOOK_SECRET:  # noqa: F405
        raise ImproperlyConfigured('STRIPE_WEBHOOK_SECRET is required when BILLING_PROVIDER=stripe.')
if not EMAIL_HOST:
    raise ImproperlyConfigured('EMAIL_HOST is required in production for verification and password reset.')
if config('REQUIRE_SENTRY', default=True, cast=bool) and not SENTRY_DSN:  # noqa: F405
    raise ImproperlyConfigured(
        'SENTRY_DSN is required in production (set REQUIRE_SENTRY=False only for constrained staging).'
    )

REQUIRE_LIVE_SMS = True  # noqa: F405
