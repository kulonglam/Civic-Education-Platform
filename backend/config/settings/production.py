from decouple import config
from corsheaders.defaults import default_headers
from django.core.exceptions import ImproperlyConfigured

from apps.core.host_utils import unique_hosts, render_hostname

from .base import *  # noqa: F403

DEBUG = False

# ALLOWED_HOSTS is set in the dashboard for custom domains. Render also injects
# RENDER_EXTERNAL_HOSTNAME (e.g. civic-education-platform-66rb.onrender.com).
ALLOWED_HOSTS = unique_hosts(
    config('ALLOWED_HOSTS', default=''),
    render_hostname(),
)

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config('CORS_ALLOWED_ORIGINS', default='').split(',')
    if origin.strip()
]

# Trust HTTPS origins for Django CSRF (admin, session cookie flows).
CSRF_TRUSTED_ORIGINS = unique_hosts(
    config('CSRF_TRUSTED_ORIGINS', default=''),
    *[f'https://{host}' for host in ALLOWED_HOSTS if host and not host.startswith('.')],
)

CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept-language',
    'x-tenant-slug',
]

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

CELERY_TASK_ALWAYS_EAGER = False

# Prefer dedicated REDIS_URL; fall back to the Celery broker for cache.
if not REDIS_URL and CELERY_BROKER_URL:  # noqa: F405
    REDIS_URL = CELERY_BROKER_URL  # noqa: F405
    CACHES = {  # noqa: F405
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL,
        }
    }

# Fail fast on boot when critical production settings are missing.
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        'ALLOWED_HOSTS must be set in production '
        '(or rely on RENDER_EXTERNAL_HOSTNAME on Render).'
    )
if not CORS_ALLOWED_ORIGINS:
    raise ImproperlyConfigured('CORS_ALLOWED_ORIGINS must be set in production.')
if SECRET_KEY.startswith('django-insecure') or SECRET_KEY.startswith('change-me'):  # noqa: F405
    raise ImproperlyConfigured('SECRET_KEY must be a secure random value in production.')
if BILLING_PROVIDER == 'dummy':  # noqa: F405
    raise ImproperlyConfigured('BILLING_PROVIDER must be "stripe" in production.')
if not CELERY_BROKER_URL:  # noqa: F405
    raise ImproperlyConfigured('CELERY_BROKER_URL is required in production.')
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
