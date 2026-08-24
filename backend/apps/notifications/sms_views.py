from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.services import require_sms
from apps.core.permissions import IsSuperAdmin
from apps.core.serializers import MessageSerializer
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgOwnerOrAdmin

from .models import SmsMessage
from .sms_serializers import BroadcastSmsSerializer, SendSmsSerializer, SmsMessageSerializer
from .sms_services import normalize_phone, queue_sms_to_phone
from .tasks import broadcast_sms_task

User = get_user_model()


class SendSmsView(APIView):
    """Send SMS to specific organization members or phone numbers."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=SendSmsSerializer, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        require_sms(organization)

        serializer = SendSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        queued = 0

        user_ids = serializer.validated_data.get('user_ids') or []
        if user_ids:
            users = User.objects.filter(
                id__in=user_ids,
                memberships__organization=organization,
            ).distinct()
            for user in users:
                if not user.phone:
                    continue
                queue_sms_to_phone(
                    user.phone,
                    message,
                    message_type=SmsMessage.TYPE_SMS,
                    user=user,
                    organization=organization,
                )
                queued += 1

        for raw_phone in serializer.validated_data.get('phones') or []:
            phone = normalize_phone(raw_phone)
            queue_sms_to_phone(
                phone,
                message,
                message_type=SmsMessage.TYPE_SMS,
                organization=organization,
            )
            queued += 1

        return Response(
            {'message': f'Queued {queued} SMS message(s).'},
            status=status.HTTP_202_ACCEPTED,
        )


class BroadcastSmsView(APIView):
    """Broadcast an SMS alert to all org members with phone numbers."""

    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=BroadcastSmsSerializer, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        require_sms(organization)

        serializer = BroadcastSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        broadcast_sms_task.delay(serializer.validated_data['message'], str(organization.id))
        return Response(
            {'message': 'SMS broadcast queued for organization members.'},
            status=status.HTTP_202_ACCEPTED,
        )


class PlatformBroadcastSmsView(APIView):
    """Platform admin: broadcast SMS to all users with phone numbers."""

    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=BroadcastSmsSerializer, responses=MessageSerializer)
    def post(self, request):
        from .tasks import send_sms_task

        serializer = BroadcastSmsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']

        queued = 0
        for user in User.objects.filter(is_active=True).exclude(phone__isnull=True).exclude(phone=''):
            queue_sms_to_phone(
                user.phone,
                message,
                message_type=SmsMessage.TYPE_BROADCAST,
                user=user,
            )
            queued += 1

        return Response(
            {'message': f'Queued {queued} civic alert SMS message(s).'},
            status=status.HTTP_202_ACCEPTED,
        )


class SmsHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = SmsMessageSerializer

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return SmsMessage.objects.none()
        return SmsMessage.all_objects.filter(organization=organization).select_related('user')
