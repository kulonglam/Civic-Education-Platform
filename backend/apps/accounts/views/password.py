"""Password reset and self-service password change."""

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.serializers import MessageSerializer
from apps.core.tasks import send_email_task
from apps.core.throttling import AuthRateThrottle

from ..serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetOtpConfirmSerializer,
    PasswordResetOtpRequestSerializer,
    PasswordResetRequestSerializer,
)

User = get_user_model()


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetRequestSerializer

    @extend_schema(request=PasswordResetRequestSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if user:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.encoding import force_bytes
            from django.utils.http import urlsafe_base64_encode

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'
            send_email_task.delay(
                'Reset your password',
                f'Click to reset your password: {reset_url}',
                [user.email],
            )
            from apps.notifications.sms_services import send_password_reset_otp

            send_password_reset_otp(user)
        return Response({'message': 'If the email exists, a reset link has been sent.'})


class PasswordResetOtpRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetOtpRequestSerializer

    @extend_schema(request=PasswordResetOtpRequestSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetOtpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from apps.notifications.sms_services import normalize_phone, send_password_reset_otp

        phone = normalize_phone(serializer.validated_data['phone'])
        user = User.objects.filter(phone=phone).first()
        if user:
            send_password_reset_otp(user)
        return Response({'message': 'If the phone number exists, a verification code has been sent.'})


class PasswordResetOtpConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetOtpConfirmSerializer

    @extend_schema(request=PasswordResetOtpConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetOtpConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(user, 'password_reset', {'via': 'sms_otp'})
        return Response({'message': 'Password reset successful.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = PasswordResetConfirmSerializer

    @extend_schema(request=PasswordResetConfirmSerializer, responses=MessageSerializer)
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        log_activity(user, 'password_reset', {})
        return Response({'message': 'Password reset successful.'})


class ChangePasswordView(APIView):
    """Allow an authenticated user to change their own password."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(
        request=inline_serializer(
            name='ChangePasswordRequest',
            fields={
                'current_password': serializers.CharField(),
                'new_password': serializers.CharField(min_length=8),
            },
        ),
        responses=MessageSerializer,
    )
    def post(self, request):
        current_password = request.data.get('current_password', '')
        new_password = request.data.get('new_password', '')

        if not current_password or not new_password:
            return Response(
                {'detail': 'Both current_password and new_password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(new_password) < 8:
            return Response(
                {'detail': 'New password must be at least 8 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not request.user.check_password(current_password):
            return Response(
                {'detail': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save(update_fields=['password'])
        from apps.accounts.session import bump_session_epoch

        bump_session_epoch(request.user)
        log_activity(request.user, 'password_changed', {})
        return Response({'message': 'Password updated successfully.'})
