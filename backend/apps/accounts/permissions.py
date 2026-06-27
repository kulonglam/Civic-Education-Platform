"""Account-level permission helpers."""

from apps.core.exceptions import MfaSetupRequired

from .mfa import user_has_mfa_enabled, user_requires_mfa


def check_mfa_enrolled(user) -> None:
    """Raise ``MfaSetupRequired`` when a privileged user has not enrolled MFA."""
    if user_requires_mfa(user) and not user_has_mfa_enabled(user):
        raise MfaSetupRequired()
