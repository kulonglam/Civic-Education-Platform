from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.tenants.permissions import IsOrgMember

from .serializers import ChatRequestSerializer, ChatResponseSerializer, TutorUsageSerializer
from .services import clear_session, get_tutor_service
from .throttling import TutorRateThrottle


class ChatView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    throttle_classes = [TutorRateThrottle]

    @extend_schema(request=ChatRequestSerializer, responses=ChatResponseSerializer)
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article_id = serializer.validated_data.get('article_id')
        result = get_tutor_service().chat(
            request.user,
            serializer.validated_data['message'],
            article_id=article_id,
        )
        return Response(result)


class ClearSessionView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses={204: None})
    def delete(self, request):
        clear_session(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TutorUsageView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = TutorUsageSerializer

    @extend_schema(responses=TutorUsageSerializer)
    def get(self, request):
        return Response(get_tutor_service().usage_summary(request.user))


class TutorAdminUsageView(APIView):
    """Platform admins: aggregate tutor usage for monitoring."""

    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(responses=dict)
    def get(self, request):
        from django.db.models import Sum

        from .models import TutorChat

        today = TutorChat.objects.filter(created_at__date=timezone.now().date())
        return Response({
            'messages_today': today.count(),
            'tokens_today': today.aggregate(total=Sum('tokens_used'))['total'] or 0,
            'active_users_today': today.values('user').distinct().count(),
        })
