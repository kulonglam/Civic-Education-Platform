"""WSGI config for Civic Education Platform."""

import os

from django.core.wsgi import get_wsgi_application

# Prefer an explicit DJANGO_SETTINGS_MODULE from the host (Render dashboard /
# Dockerfile). Fall back to development only for local runs.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_wsgi_application()
