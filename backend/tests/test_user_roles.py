import pytest
from rest_framework import status

from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestUserRoleUpdate:
    def test_admin_can_promote_to_editor(self, api_client, admin_user, citizen_user, org):
        Membership.objects.get_or_create(organization=org, user=citizen_user, defaults={'role': Membership.MEMBER})
        bind_client_to_org(api_client, admin_user, org)

        response = api_client.patch(
            f'/api/users/{citizen_user.id}/role/',
            {'role': 'editor'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role']['name'] == 'editor'
        citizen_user.refresh_from_db()
        assert citizen_user.role.name == 'editor'

    def test_admin_can_promote_to_moderator(self, api_client, admin_user, editor_user, org):
        Membership.objects.get_or_create(organization=org, user=editor_user, defaults={'role': Membership.MEMBER})
        bind_client_to_org(api_client, admin_user, org)

        response = api_client.patch(
            f'/api/users/{editor_user.id}/role/',
            {'role': 'moderator'},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['role']['name'] == 'moderator'

    def test_moderator_cannot_change_roles(self, api_client, moderator_user, citizen_user, org):
        Membership.objects.get_or_create(organization=org, user=citizen_user, defaults={'role': Membership.MEMBER})
        bind_client_to_org(api_client, moderator_user, org)

        response = api_client.patch(
            f'/api/users/{citizen_user.id}/role/',
            {'role': 'editor'},
            format='json',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_cannot_change_own_role(self, api_client, admin_user, org):
        bind_client_to_org(api_client, admin_user, org)

        response = api_client.patch(
            f'/api/users/{admin_user.id}/role/',
            {'role': 'citizen'},
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_change_user_outside_org(self, api_client, admin_user, org, django_user_model):
        outsider = django_user_model.objects.create_user(
            email='outsider@roles.test',
            password='TestPass123!',
            first_name='Out',
            last_name='Side',
        )
        bind_client_to_org(api_client, admin_user, org)

        response = api_client.patch(
            f'/api/users/{outsider.id}/role/',
            {'role': 'editor'},
            format='json',
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUserSuspendIsolation:
    def test_moderator_can_suspend_org_member(self, api_client, moderator_user, org, citizen_user):
        bind_client_to_org(api_client, moderator_user, org)

        response = api_client.post(f'/api/users/{citizen_user.id}/suspend/')
        assert response.status_code == status.HTTP_200_OK
        citizen_user.refresh_from_db()
        assert citizen_user.is_suspended is True

    def test_cannot_suspend_user_outside_org(self, api_client, moderator_user, org, django_user_model):
        outsider = django_user_model.objects.create_user(
            email='outsider@suspend.test',
            password='TestPass123!',
            first_name='Out',
            last_name='Side',
        )
        bind_client_to_org(api_client, moderator_user, org)

        response = api_client.post(f'/api/users/{outsider.id}/suspend/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        outsider.refresh_from_db()
        assert outsider.is_suspended is False

    def test_cannot_unsuspend_user_outside_org(self, api_client, moderator_user, org, django_user_model):
        outsider = django_user_model.objects.create_user(
            email='outsider@unsuspend.test',
            password='TestPass123!',
            first_name='Out',
            last_name='Side',
        )
        outsider.is_suspended = True
        outsider.save(update_fields=['is_suspended'])
        bind_client_to_org(api_client, moderator_user, org)

        response = api_client.post(f'/api/users/{outsider.id}/unsuspend/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
        outsider.refresh_from_db()
        assert outsider.is_suspended is True
