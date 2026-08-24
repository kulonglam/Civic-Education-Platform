from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.permissions import IsOrgMember

from .serializers import GamificationSummarySerializer
from .services import build_gamification_summary, build_leaderboard


class GamificationMeView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses=GamificationSummarySerializer)
    def get(self, request):
        return Response(build_gamification_summary(request.user))


class GamificationLeaderboardView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get(self, request):
        try:
            limit = int(request.query_params.get('limit', 20))
        except (TypeError, ValueError):
            limit = 20
        return Response(build_leaderboard(request.user, limit=limit))
