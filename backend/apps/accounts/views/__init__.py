"""Account views.

Split into cohesive submodules; every public view is re-exported here so
``from apps.accounts.views import <View>`` keeps working.
"""

from .auth import EmailTokenObtainPairView, LoginView, LogoutView, RegisterView
from .mfa import MfaSetupView, MfaVerifyLoginView
from .password import (
    ChangePasswordView,
    PasswordResetConfirmView,
    PasswordResetOtpConfirmView,
    PasswordResetOtpRequestView,
    PasswordResetRequestView,
)
from .profile import AvatarUploadView, DeactivateAccountView, MyDataExportView, ProfileView
from .user_management import (
    SuspendUserView,
    UnsuspendUserView,
    UpdateUserRoleView,
    UserListView,
)
from .verification import (
    PhoneVerifyConfirmView,
    PhoneVerifySendView,
    ResendVerificationEmailView,
    VerifyEmailView,
)

__all__ = [
    'AvatarUploadView',
    'ChangePasswordView',
    'DeactivateAccountView',
    'EmailTokenObtainPairView',
    'LoginView',
    'LogoutView',
    'MfaSetupView',
    'MfaVerifyLoginView',
    'MyDataExportView',
    'PasswordResetConfirmView',
    'PasswordResetOtpConfirmView',
    'PasswordResetOtpRequestView',
    'PasswordResetRequestView',
    'PhoneVerifyConfirmView',
    'PhoneVerifySendView',
    'ProfileView',
    'RegisterView',
    'ResendVerificationEmailView',
    'SuspendUserView',
    'UnsuspendUserView',
    'UpdateUserRoleView',
    'UserListView',
    'VerifyEmailView',
]
