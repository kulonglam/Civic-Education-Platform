from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .search import global_search


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    parameters=[
        OpenApiParameter(name='q', type=str, description='Search query (min 2 characters)'),
        OpenApiParameter(name='limit', type=int, description='Max results per content type (default 8)'),
    ],
)
class GlobalSearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        try:
            limit = int(request.query_params.get('limit', 8))
        except (TypeError, ValueError):
            limit = 8
        return Response(global_search(query, limit=limit))
