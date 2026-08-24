from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.tenants.services import get_user_organization

from .session import get_session_epoch


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role.name
        token['sv'] = get_session_epoch(user)
        organization = get_user_organization(user)
        if organization is not None:
            token['org'] = str(organization.id)
            token['org_slug'] = organization.slug
        return token


def issue_tokens_for_user(user, *, extra_claims=None, lifetime=None, organization=None):
    """Build access/refresh JWTs, optionally with extra claims and a short lifetime."""
    refresh = EmailTokenObtainPairSerializer.get_token(user)
    extra_claims = extra_claims or {}
    if organization is not None:
        extra_claims = {
            **extra_claims,
            'org': str(organization.id),
            'org_slug': organization.slug,
        }
    for key, value in extra_claims.items():
        refresh[key] = value
    if lifetime is not None:
        refresh.set_exp(lifetime=lifetime)
    access = refresh.access_token
    for key, value in extra_claims.items():
        access[key] = value
    if lifetime is not None:
        access.set_exp(lifetime=lifetime)
    return {'access': str(access), 'refresh': str(refresh)}
