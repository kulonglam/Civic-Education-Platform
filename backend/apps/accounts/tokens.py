from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.tenants.services import get_user_organization


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role.name
        organization = get_user_organization(user)
        if organization is not None:
            token['org'] = str(organization.id)
            token['org_slug'] = organization.slug
        return token
