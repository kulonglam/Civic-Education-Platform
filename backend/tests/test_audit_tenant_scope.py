import pytest
from rest_framework import status

from apps.audit.models import ActivityLog
from apps.tenants.models import Membership
from apps.tenants.services import create_organization_with_owner
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestAuditLogTenantScope:
    def test_logs_filtered_by_current_organization(self, api_client, moderator_user, org, citizen_user):
        other_org = create_organization_with_owner(
            name='Other Org',
            owner=citizen_user,
            slug='other-org',
        )
        ActivityLog.objects.create(
            organization=org,
            user=citizen_user,
            activity_type='article_created',
            metadata={'article_id': 'a1'},
        )
        ActivityLog.objects.create(
            organization=other_org,
            user=citizen_user,
            activity_type='article_created',
            metadata={'article_id': 'a2'},
        )

        bind_client_to_org(api_client, moderator_user, org, membership_role=Membership.ADMIN)
        response = api_client.get('/api/audit/logs/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert results[0]['metadata']['article_id'] == 'a1'

    def test_logs_without_org_context_returns_all(self, api_client, moderator_user, org, citizen_user):
        other_org = create_organization_with_owner(
            name='Other Org 2',
            owner=citizen_user,
            slug='other-org-2',
        )
        ActivityLog.objects.create(
            organization=org,
            activity_type='admin_action',
            metadata={},
        )
        ActivityLog.objects.create(
            organization=other_org,
            activity_type='admin_action',
            metadata={},
        )

        api_client.force_authenticate(user=moderator_user)
        response = api_client.get('/api/audit/logs/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) >= 2
