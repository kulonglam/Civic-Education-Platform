from decouple import config
from corsheaders.defaults import default_headers

from apps.core.host_utils import unique_hosts, render_hostname

from .base import *  # noqa: F403

DEBUG = True
ALLOWED_HOSTS = unique_hosts(
    config('ALLOWED_HOSTS', default='localhost,127.0.0.1'),
    render_hostname(),
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
_email_host = config('EMAIL_HOST', default='').strip()
if _email_host:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = _email_host
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in config(
        'CORS_ALLOWED_ORIGINS',
        default='http://localhost:5173,http://127.0.0.1:5173',
    ).split(',')
    if origin.strip()
]

# Dev-friendly: allow SPA requests from any origin (still echoes the request origin).
CORS_ALLOW_ALL_ORIGINS = config('CORS_ALLOW_ALL_ORIGINS', default=True, cast=bool)

# Frontend sends these on API requests (see frontend/src/lib/api.js).
CORS_ALLOW_HEADERS = list(default_headers) + [
    'accept-language',
    'x-tenant-slug',
]
