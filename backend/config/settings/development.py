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
