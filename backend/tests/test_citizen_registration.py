import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.tenants.models import Membership, Organization
from apps.tenants.services import create_organization_with_owner


@pytest.fixture
def public_org(db, admin_user):
    from django.conf import settings

    slug = getattr(settings, 'PUBLIC_ORGANIZATION_SLUG', 'platform-demo')
    org = Organization.objects.filter(slug=slug).first()
    if org is None:
        org = create_organization_with_owner(
            name='Platform Demo',
            owner=admin_user,
            slug=slug,
        )
    return org


@pytest.mark.django_db
class TestCitizenRegistration:
    def test_register_citizen_joins_public_org(self, api_client, roles, public_org):
        response = api_client.post('/api/auth/register/', {
            'email': 'learner@test.com',
            'first_name': 'Learner',
            'last_name': 'Citizen',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'account_type': 'citizen',
        })
        assert response.status_code == status.HTTP_201_CREATED

        from apps.accounts.models import User

        user = User.objects.get(email='learner@test.com')
        assert user.role.name == Role.CITIZEN
        assert not Organization.objects.filter(
            memberships__user=user,
            memberships__role=Membership.OWNER,
        ).exists()
        assert Membership.objects.filter(
            organization=public_org,
            user=user,
            role=Membership.MEMBER,
        ).exists()

    def test_register_defaults_to_citizen(self, api_client, roles, public_org):
        response = api_client.post('/api/auth/register/', {
            'email': 'default@test.com',
            'first_name': 'Default',
            'last_name': 'Citizen',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
        })
        assert response.status_code == status.HTTP_201_CREATED
        from apps.accounts.models import User

        user = User.objects.get(email='default@test.com')
        assert user.role.name == Role.CITIZEN
        assert Membership.objects.filter(organization=public_org, user=user).exists()
