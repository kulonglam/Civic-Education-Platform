"""Redirect SPA deep links that accidentally hit the API hostname."""

from urllib.parse import urlparse

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.views import View

from apps.core.host_utils import production_public_origin


class FrontendVerifyEmailRedirect(View):
    """Send ``/verify-email/<token>/`` on the API host to the SPA.

    Mail links are built as ``{FRONTEND_URL}/verify-email/{token}``. If
    FRONTEND_URL was set to the API, or a user opens the API host, Django
    would otherwise 404 with ``Not Found``.
    """

    def get(self, request, token: str):
        frontend = production_public_origin(getattr(settings, 'FRONTEND_URL', ''))
        if not frontend:
            return HttpResponseNotFound('Not Found')
        front_host = (urlparse(frontend).hostname or '').lower()
        this_host = (request.get_host() or '').split(':')[0].lower()
        if not front_host or front_host == this_host:
            return HttpResponseNotFound('Not Found')
        return HttpResponseRedirect(f'{frontend}/verify-email/{token}')
