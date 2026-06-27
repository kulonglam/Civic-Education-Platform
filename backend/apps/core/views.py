import logging

from django.core.cache import cache
from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

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

        healthy = all(v == 'ok' for v in checks.values())
        return Response(
            {'status': 'ready' if healthy else 'degraded', **checks},
            status=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
