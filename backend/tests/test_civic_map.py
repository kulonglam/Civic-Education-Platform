from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from apps.accounts.models import UserProfile
from apps.engagement.models import CivicEvent
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


def _make_event(org, **overrides):
    starts = timezone.now() + timedelta(days=7)
    defaults = {
        'organization': org,
        'title': 'Mapped civic event',
        'description': 'Public meeting.',
        'location': 'Juba',
        'region': 'central_equatoria',
        'kind': CivicEvent.KIND_COMMUNITY_MEETING,
        'starts_at': starts,
        'status': CivicEvent.STATUS_PUBLISHED,
    }
    defaults.update(overrides)
    return CivicEvent.objects.create(**defaults)


@pytest.mark.django_db
class TestCivicMap:
    def test_public_map_lists_published_events(self, api_client, org):
        _make_event(org)
        _make_event(org, title='Draft', status=CivicEvent.STATUS_DRAFT)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/maps/civic/')
        assert response.status_code == status.HTTP_200_OK
        titles = [row['title'] for row in response.data['events']]
        assert 'Mapped civic event' in titles
        assert 'Draft' not in titles
        central = next(row for row in response.data['regions'] if row['key'] == 'central_equatoria')
        assert central['upcoming_event_count'] == 1

    def test_hides_small_learner_counts(self, api_client, org, citizen_user):
        UserProfile.objects.update_or_create(
            user=citizen_user,
            defaults={'region': 'jonglei'},
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/maps/civic/')
        jonglei = next(row for row in response.data['regions'] if row['key'] == 'jonglei')
        assert jonglei['learner_count_hidden'] is True
        assert jonglei['learner_count'] is None

    def test_rejects_unknown_event_region(self, api_client, org, editor_user):
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        starts = timezone.now() + timedelta(days=7)
        response = api_client.post(
            '/api/events/',
            {
                'title': 'Unknown region event',
                'description': 'Should be rejected.',
                'kind': CivicEvent.KIND_WORKSHOP,
                'starts_at': starts.isoformat(),
                'region': 'nairobi',
                'status': CivicEvent.STATUS_DRAFT,
            },
            format='json',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'region' in response.data
