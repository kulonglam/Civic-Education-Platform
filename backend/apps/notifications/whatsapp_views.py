import hashlib
import hmac

from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseForbidden
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.services import require_sms
from apps.core.branding import PLATFORM_NAME
from apps.core.permissions import IsSuperAdmin
from apps.core.serializers import MessageSerializer
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgOwnerOrAdmin

from .models import WhatsAppMessage
from .whatsapp_providers import whatsapp_cloud_configured, whatsapp_to_e164
from .whatsapp_serializers import (
    BroadcastWhatsAppSerializer,
    SendWhatsAppSerializer,
    WhatsAppMessageSerializer,
)
from .whatsapp_services import queue_whatsapp_to_phone, record_inbound_whatsapp
from .tasks import broadcast_whatsapp_task

User = get_user_model()


class WhatsAppStatusView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(responses=MessageSerializer)
    def get(self, request):
        display = getattr(settings, 'WHATSAPP_DISPLAY_NUMBER', '') or ''
        return Response({
            'share_enabled': True,
            'cloud_configured': whatsapp_cloud_configured(),
            'display_number': display,
            'click_to_chat_url': f'https://wa.me/{display.lstrip("+")}' if display else '',
        })


class SendWhatsAppView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=SendWhatsAppSerializer, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        require_sms(organization)

        serializer = SendWhatsAppSerializer(data=request.data)
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
                queue_whatsapp_to_phone(
                    user.phone,
                    message,
                    message_type=WhatsAppMessage.TYPE_ALERT,
                    user=user,
                    organization=organization,
                )
                queued += 1

        for raw_phone in serializer.validated_data.get('phones') or []:
            phone = whatsapp_to_e164(raw_phone)
            queue_whatsapp_to_phone(
                phone,
                message,
                message_type=WhatsAppMessage.TYPE_ALERT,
                organization=organization,
            )
            queued += 1

        return Response(
            {'message': f'Queued {queued} WhatsApp message(s).'},
            status=status.HTTP_202_ACCEPTED,
        )


class BroadcastWhatsAppView(APIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]

    @extend_schema(request=BroadcastWhatsAppSerializer, responses=MessageSerializer)
    def post(self, request):
        organization = get_current_organization()
        require_sms(organization)
        serializer = BroadcastWhatsAppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        broadcast_whatsapp_task.delay(serializer.validated_data['message'], str(organization.id))
        return Response(
            {'message': 'WhatsApp broadcast queued for organization members.'},
            status=status.HTTP_202_ACCEPTED,
        )


class PlatformBroadcastWhatsAppView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @extend_schema(request=BroadcastWhatsAppSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = BroadcastWhatsAppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.validated_data['message']
        queued = 0
        for user in User.objects.filter(is_active=True).exclude(phone__isnull=True).exclude(phone=''):
            queue_whatsapp_to_phone(
                user.phone,
                message,
                message_type=WhatsAppMessage.TYPE_BROADCAST,
                user=user,
            )
            queued += 1
        return Response(
            {'message': f'Queued {queued} civic WhatsApp message(s).'},
            status=status.HTTP_202_ACCEPTED,
        )


class WhatsAppHistoryView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsOrgOwnerOrAdmin]
    serializer_class = WhatsAppMessageSerializer

    def get_queryset(self):
        organization = get_current_organization()
        if organization is None:
            return WhatsAppMessage.objects.none()
        return WhatsAppMessage.all_objects.filter(organization=organization).select_related('user')


def _valid_meta_signature(request) -> bool:
    secret = getattr(settings, 'WHATSAPP_APP_SECRET', '') or ''
    if not secret:
        return True
    header = request.headers.get('X-Hub-Signature-256') or ''
    if not header.startswith('sha256='):
        return False
    expected = hmac.new(secret.encode('utf-8'), request.body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(header.removeprefix('sha256='), expected)


class WhatsAppWebhookView(APIView):
    """Meta WhatsApp Cloud API webhook (verify + inbound)."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        mode = request.query_params.get('hub.mode')
        token = request.query_params.get('hub.verify_token')
        challenge = request.query_params.get('hub.challenge', '')
        expected = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '') or ''
        if mode == 'subscribe' and expected and token == expected:
            return HttpResponse(challenge, content_type='text/plain')
        return HttpResponseForbidden('Invalid verify token')

    def post(self, request):
        if not _valid_meta_signature(request):
            return HttpResponseForbidden('Invalid signature')
        payload = request.data if isinstance(request.data, dict) else {}
        inbound_count = 0
        for entry in payload.get('entry') or []:
            for change in entry.get('changes') or []:
                value = change.get('value') or {}
                for message in value.get('messages') or []:
                    if message.get('type') != 'text':
                        continue
                    body = ((message.get('text') or {}).get('body') or '').strip()
                    sender = message.get('from') or ''
                    if not body or not sender:
                        continue
                    inbound = record_inbound_whatsapp(
                        phone=sender if sender.startswith('+') else f'+{sender}',
                        message=body,
                        provider_reference=message.get('id') or '',
                    )
                    inbound_count += 1
                    _auto_reply(sender, organization=inbound.organization if inbound else None)
        return Response({'received': inbound_count})


def _auto_reply(sender: str, *, organization=None) -> None:
    if organization is None:
        return
    frontend = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    text = (
        f'{PLATFORM_NAME}: thanks for writing. Open civic lessons, events, and the map at {frontend} '
        f'or ask a question in the AI tutor.'
    )
    try:
        queue_whatsapp_to_phone(
            f'+{sender.lstrip("+")}',
            text,
            message_type=WhatsAppMessage.TYPE_ALERT,
            organization=organization,
        )
    except ValueError:
        return
