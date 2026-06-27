from drf_spectacular.utils import extend_schema
from django.conf import settings
from rest_framework import generics, serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.core.serializers import MessageSerializer
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgOwnerOrAdmin

from .extra_serializers import BroadcastNotificationSerializer, WebPushSubscribeSerializer
from .models import Notification, WebPushSubscription
from .push_services import cleanup_push_subscriptions, push_subscription_stats
from .services import notify_all_users


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'created_at']


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_read']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    @extend_schema(request=None, responses=NotificationSerializer)
    def patch(self, request, id):
        try:
            notification = Notification.objects.get(id=id, user=request.user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response(NotificationSerializer(notification).data)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    @extend_schema(request=None, responses=MessageSerializer)
    def patch(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read.'})


class BroadcastNotificationView(APIView):
    """Org admin: send an in-app announcement to all org members."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=BroadcastNotificationSerializer, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        if organization is None:
            return Response({'detail': 'Organization context required.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BroadcastNotificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        notify_all_users(
            data['notification_type'],
            data['title'],
            data['message'],
            organization_id=str(organization.id),
        )
        return Response(
            {'message': 'In-app announcement queued for organization members.'},
            status=status.HTTP_202_ACCEPTED,
        )


class WebPushSubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=WebPushSubscribeSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = WebPushSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        keys = serializer.validated_data['keys']
        WebPushSubscription.objects.update_or_create(
            endpoint=serializer.validated_data['endpoint'],
            defaults={
                'user': request.user,
                'p256dh': keys['p256dh'],
                'auth': keys['auth'],
            },
        )
        return Response({'message': 'Push subscription saved.'}, status=status.HTTP_201_CREATED)

    @extend_schema(request=WebPushSubscribeSerializer, responses=MessageSerializer)
    def delete(self, request):
        serializer = WebPushSubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        WebPushSubscription.objects.filter(
            user=request.user,
            endpoint=serializer.validated_data['endpoint'],
        ).delete()
        return Response({'message': 'Push subscription removed.'})


class PushSubscriptionStatsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    @extend_schema(responses={200: dict})
    def get(self, request):
        return Response(push_subscription_stats())


class PushSubscriptionCleanupView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = MessageSerializer

    @extend_schema(request=None, responses=MessageSerializer)
    def post(self, request):
        from .tasks import cleanup_push_subscriptions_task

        if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', True):
            result = cleanup_push_subscriptions()
        else:
            async_result = cleanup_push_subscriptions_task.delay()
            result = async_result.get(timeout=30)
        total_deleted = result['deleted_inactive_user'] + result['deleted_older_than_days']
        return Response(
            {
                'message': f'Removed {total_deleted} stale push subscription(s).',
                'details': result,
            }
        )
