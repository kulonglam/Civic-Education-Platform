from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.permissions import IsOrgMember

from .serializers import GamificationSummarySerializer
from .services import build_gamification_summary


class GamificationMeView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses=GamificationSummarySerializer)
    def get(self, request):
        return Response(build_gamification_summary(request.user))
