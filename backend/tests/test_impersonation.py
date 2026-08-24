import pytest
from rest_framework import status

from apps.audit.models import ActivityLog
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestSupportImpersonation:
    def test_super_admin_impersonates_member_and_exits(
        self, api_client, super_admin_user, citizen_user, org,
    ):
        bind_client_to_org(api_client, super_admin_user, org, membership_role=Membership.ADMIN)
        start = api_client.post(
            f'/api/organization/platform/orgs/{org.id}/impersonate/',
            {'user_id': str(citizen_user.id)},
            format='json',
        )
        assert start.status_code == status.HTTP_200_OK, start.data
        assert start.data['target']['email'] == citizen_user.email
        from rest_framework_simplejwt.tokens import AccessToken

        token = AccessToken(start.data['access'])
        assert str(token['impersonator_id']) == str(super_admin_user.id)
        assert str(token['user_id']) == str(citizen_user.id)
        assert ActivityLog.objects.filter(activity_type='impersonation_started').exists()

        api_client.force_authenticate(user=None)
        api_client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {start.data["access"]}',
            HTTP_X_TENANT_SLUG=org.slug,
        )
        profile = api_client.get('/api/users/profile/')
        assert profile.status_code == status.HTTP_200_OK
        assert profile.data['email'] == citizen_user.email

        ended = api_client.post('/api/organization/platform/impersonate/exit/')
        assert ended.status_code == status.HTTP_200_OK, ended.data
        restored = AccessToken(ended.data['access'])
        assert str(restored['user_id']) == str(super_admin_user.id)
        assert restored.get('impersonator_id') in (None, '')
        assert ActivityLog.objects.filter(activity_type='impersonation_ended').exists()

    def test_cannot_impersonate_super_admin(
        self, api_client, super_admin_user, django_user_model, roles, org,
    ):
        from apps.accounts.models import Role

        other = django_user_model.objects.create_user(
            email='other-super@test.com',
            password='TestPass123!',
            first_name='Other',
            last_name='Super',
            role=Role.objects.get(name='super_admin'),
        )
        Membership.objects.create(organization=org, user=other, role=Membership.ADMIN)
        bind_client_to_org(api_client, super_admin_user, org, membership_role=Membership.ADMIN)
        response = api_client.post(
            f'/api/organization/platform/orgs/{org.id}/impersonate/',
            {'user_id': str(other.id)},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
