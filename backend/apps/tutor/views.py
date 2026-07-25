from django.http import StreamingHttpResponse
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.tenants.permissions import IsOrgMember

from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    TutorSessionSerializer,
    TutorSessionSummarySerializer,
    TutorUsageSerializer,
)
from .services import (
    clear_session,
    get_active_session_payload,
    get_chat_session_history,
    get_tutor_service,
    list_chat_sessions,
)
from .throttling import TutorRateThrottle


def _sse_event(event: str, data: dict) -> str:
    import json

    return f'event: {event}\ndata: {json.dumps(data)}\n\n'


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


class ChatStreamView(APIView):
    """Server-sent events stream for tutor replies."""

    permission_classes = [IsAuthenticated, IsOrgMember]
    throttle_classes = [TutorRateThrottle]

    @extend_schema(request=ChatRequestSerializer, responses={200: str})
    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article_id = serializer.validated_data.get('article_id')
        service = get_tutor_service()

        def event_stream():
            for item in service.chat_stream(
                request.user,
                serializer.validated_data['message'],
                article_id=article_id,
            ):
                yield _sse_event(item['event'], item['data'])

        response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        return response


class SessionView(APIView):
    """Active in-memory tutor session (Redis, ~1 hour TTL)."""

    permission_classes = [IsAuthenticated, IsOrgMember]

    @extend_schema(responses=TutorSessionSerializer)
    def get(self, request):
        return Response(get_active_session_payload(request.user))

    @extend_schema(responses={204: None})
    def delete(self, request):
        clear_session(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses=TutorSessionSummarySerializer(many=True))
class ChatHistoryListView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get(self, request):
        return Response(list_chat_sessions(request.user))


@extend_schema(responses=TutorSessionSerializer)
class ChatHistoryDetailView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get(self, request, session_id):
        payload = get_chat_session_history(request.user, session_id)
        if payload is None:
            return Response({'detail': 'Session not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(payload)


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
