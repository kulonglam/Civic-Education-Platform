"""Email and phone verification."""

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
from apps.core.tasks import send_email_task
from apps.core.throttling import AuthRateThrottle

from ..models import EmailVerificationToken
from ..serializers import PhoneVerifyConfirmSerializer


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
        send_email_task.delay(
            f'Verify your {PLATFORM_NAME} account',
            f'Click to verify your email: {verify_url}',
            [user.email],
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
        from apps.notifications.sms_services import send_phone_verify_otp

        send_phone_verify_otp(user)
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
