from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from ..sso_views import SsoCallbackView, SsoLoginView, SsoStatusView
from ..views import (
    ChangePasswordView,
    LoginView,
    LogoutView,
    MfaSetupView,
    MfaVerifyLoginView,
    PasswordResetConfirmView,
    PasswordResetOtpConfirmView,
    PasswordResetOtpRequestView,
    PasswordResetRequestView,
    PhoneVerifyConfirmView,
    PhoneVerifySendView,
    RegisterView,
    ResendVerificationEmailView,
    VerifyEmailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth-register'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password/reset/otp/', PasswordResetOtpRequestView.as_view(), name='password-reset-otp'),
    path('password/reset/otp/confirm/', PasswordResetOtpConfirmView.as_view(), name='password-reset-otp-confirm'),
    path('phone/verify/send/', PhoneVerifySendView.as_view(), name='phone-verify-send'),
    path('phone/verify/confirm/', PhoneVerifyConfirmView.as_view(), name='phone-verify-confirm'),
    path('verify-email/resend/', ResendVerificationEmailView.as_view(), name='verify-email-resend'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('password/change/', ChangePasswordView.as_view(), name='password-change'),
    path('mfa/setup/', MfaSetupView.as_view(), name='auth-mfa-setup'),
    path('mfa/verify/', MfaVerifyLoginView.as_view(), name='auth-mfa-verify'),
    path('sso/status/', SsoStatusView.as_view(), name='auth-sso-status'),
    path('sso/login/', SsoLoginView.as_view(), name='auth-sso-login'),
    path('sso/callback/', SsoCallbackView.as_view(), name='auth-sso-callback'),
]
