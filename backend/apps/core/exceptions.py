from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.views import exception_handler

from .security import log_security_event


class MfaSetupRequired(APIException):
    status_code = 403
    default_detail = 'Multi-factor authentication must be enabled for your account.'
    default_code = 'mfa_setup_required'


def custom_exception_handler(exc, context):
    """Log permission denials and MFA setup blocks as security events."""
    request = context.get('request')
    if isinstance(exc, PermissionDenied):
        log_security_event(
            'permission_denied',
            request=request,
            user=getattr(request, 'user', None),
            detail={'reason': str(exc.detail) if hasattr(exc, 'detail') else None},
        )
    elif isinstance(exc, MfaSetupRequired):
        log_security_event(
            'mfa_setup_required',
            request=request,
            user=getattr(request, 'user', None),
        )

    return exception_handler(exc, context)
