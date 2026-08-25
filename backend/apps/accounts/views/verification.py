"""Email and phone verification."""

import logging
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.branding import PLATFORM_NAME
from apps.core.serializers import MessageSerializer
from apps.core.tasks import send_transactional_email
from apps.core.throttling import AuthRateThrottle

from ..models import EmailVerificationToken
from ..serializers import PhoneVerifyConfirmSerializer

logger = logging.getLogger(__name__)


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(responses=MessageSerializer)
    def get(self, request, token):
        try:
            verification = EmailVerificationToken.objects.select_related('user').get(
                token=token, used=False, expires_at__gt=timezone.now()
            )
        except EmailVerificationToken.DoesNotExist:
            return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
        user = verification.user
        user.email_verified = True
        user.save(update_fields=['email_verified'])
        verification.used = True
        verification.save(update_fields=['used'])
        log_activity(user, 'email_verified', {})
        return Response({'message': 'Email verified successfully.'})


class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=MessageSerializer)
    def post(self, request):
        user = request.user
        if user.email_verified:
            return Response({'message': 'Email is already verified.'})
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        verify_url = f'{settings.FRONTEND_URL}/verify-email/{token}'
        try:
            send_transactional_email(
                f'Verify your {PLATFORM_NAME} account',
                f'Click to verify your email: {verify_url}',
                [user.email],
            )
        except Exception:
            logger.exception('Resend verification email failed')
            return Response(
                {
                    'detail': (
                        'Could not send the verification email. Configure SMTP on the API '
                        '(EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, DEFAULT_FROM_EMAIL).'
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return Response({'message': 'Verification email sent.'})


class PhoneVerifySendView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(responses=MessageSerializer)
    def post(self, request):
        user = request.user
        if not user.phone:
            return Response(
                {'detail': 'Add a phone number to your profile first.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.phone_verified:
            return Response({'message': 'Phone number is already verified.'})
        sms_live = (
            getattr(settings, 'SMS_PROVIDER', 'dummy') == 'africastalking'
            and getattr(settings, 'AT_USERNAME', '')
            and getattr(settings, 'AT_API_KEY', '')
        )
        if not sms_live and getattr(settings, 'REQUIRE_LIVE_SMS', False):
            return Response(
                {
                    'detail': (
                        'SMS is not configured on this server, so no code was delivered. '
                        "Set SMS_PROVIDER=africastalking with AT_USERNAME and AT_API_KEY "
                        "(Africa's Talking). Phone numbers must be South Sudan (+211)."
                    )
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        from apps.notifications.models import SmsMessage
        from apps.notifications.sms_services import send_phone_verify_otp

        sms_log = send_phone_verify_otp(user)
        if sms_log is not None and sms_log.status == SmsMessage.STATUS_FAILED:
            return Response(
                {'detail': sms_log.error_detail or 'The SMS provider rejected the message.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({'message': 'Verification code sent to your phone.'})


class PhoneVerifyConfirmView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(request=PhoneVerifyConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PhoneVerifyConfirmSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.phone_verified = True
        user.save(update_fields=['phone_verified'])
        log_activity(user, 'phone_verified', {})
        return Response({'message': 'Phone number verified successfully.'})
