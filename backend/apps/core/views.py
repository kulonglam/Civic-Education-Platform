import logging

from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin

from .models import SecurityEvent
from .serializers import HealthSerializer

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Liveness probe: confirms the process is up and serving."""

    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    @extend_schema(responses=HealthSerializer)
    def get(self, request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class ReadinessCheckView(APIView):
    """Readiness probe: verifies dependencies (database, cache) are reachable."""

    permission_classes = [AllowAny]
    serializer_class = HealthSerializer

    @extend_schema(responses=HealthSerializer)
    def get(self, request):
        checks = {}

        try:
            connections['default'].cursor().execute('SELECT 1')
            checks['database'] = 'ok'
        except OperationalError as exc:
            logger.error('Readiness DB check failed: %s', exc)
            checks['database'] = 'error'

        try:
            cache.set('readiness_probe', '1', 5)
            checks['cache'] = 'ok' if cache.get('readiness_probe') == '1' else 'error'
        except Exception as exc:  # noqa: BLE001 - cache backend errors vary
            logger.error('Readiness cache check failed: %s', exc)
            checks['cache'] = 'error'

        from django.conf import settings as dj_settings

        checks['sentry_configured'] = 'ok' if getattr(dj_settings, 'SENTRY_DSN', '') else 'unset'
        # Sentry is recommended but not required for process readiness (liveness of deps).
        healthy = checks.get('database') == 'ok' and checks.get('cache') == 'ok'
        return Response(
            {
                'status': 'ready' if healthy else 'degraded',
                **checks,
                'observability': {
                    'sentry': checks['sentry_configured'],
                    'health': '/api/health/',
                    'ready': '/api/ready/',
                    'slo': '/api/organization/platform/slo/',
                    'security_events': '/api/security/events/',
                },
            },
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class SecurityEventListView(APIView):
    """Platform admin: recent security events (failed logins, MFA, etc.)."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        qs = SecurityEvent.objects.all()
        event_type = (request.query_params.get('event_type') or '').strip()
        if event_type:
            qs = qs.filter(event_type=event_type)
        try:
            limit = min(int(request.query_params.get('page_size') or 50), 200)
        except (TypeError, ValueError):
            limit = 50
        rows = []
        for event in qs[:limit]:
            rows.append({
                'id': str(event.id),
                'event_type': event.event_type,
                'user_id': str(event.user_id) if event.user_id else None,
                'user_email': event.user_email,
                'ip_address': event.ip_address,
                'path': event.path,
                'method': event.method,
                'detail': event.detail,
                'created_at': event.created_at,
            })
        return Response({'results': rows, 'count': len(rows)})
