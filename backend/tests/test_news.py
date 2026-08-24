import pytest
from django.utils import timezone
from rest_framework import status

from apps.engagement.models import CivicNews
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


def _make_news(org, **overrides):
    defaults = {
        'organization': org,
        'title': 'Sample civic notice',
        'body': 'Body text for a civic information item.',
        'topic': CivicNews.TOPIC_ANNOUNCEMENT,
        'claim_type': CivicNews.CLAIM_EDUCATIONAL,
        'status': CivicNews.STATUS_PUBLISHED,
        'published_at': timezone.now(),
    }
    defaults.update(overrides)
    return CivicNews.objects.create(**defaults)


@pytest.mark.django_db
class TestCivicNews:
    def test_public_list_is_allow_any(self, api_client, org):
        _make_news(org, title='Published notice')
        _make_news(org, title='Hidden draft', status=CivicNews.STATUS_DRAFT, published_at=None)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/news/')
        assert response.status_code == status.HTTP_200_OK
        titles = [row['title'] for row in response.data['results']]
        assert 'Published notice' in titles
        assert 'Hidden draft' not in titles

    def test_payload_includes_claim_and_topic(self, api_client, org):
        item = _make_news(
            org,
            title='Constitution remains supreme law',
            topic=CivicNews.TOPIC_LAW_POLICY,
            claim_type=CivicNews.CLAIM_VERIFIED,
            source_name='Transitional Constitution, 2011',
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/news/{item.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['claim_type'] == 'verified_fact'
        assert response.data['topic'] == 'law_policy'
        assert response.data['source_name'] == 'Transitional Constitution, 2011'

    def test_filter_by_claim_type(self, api_client, org):
        _make_news(org, title='Fact item', claim_type=CivicNews.CLAIM_VERIFIED, source_name='Gazette')
        _make_news(org, title='Opinion item', claim_type=CivicNews.CLAIM_OPINION)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/news/', {'claim_type': 'opinion'})
        titles = [row['title'] for row in response.data['results']]
        assert titles == ['Opinion item']

    def test_verified_fact_requires_source(self, api_client, org, editor_user):
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        response = api_client.post('/api/news/', {
            'title': 'Unsourced fact',
            'body': 'This should be rejected.',
            'topic': CivicNews.TOPIC_ANNOUNCEMENT,
            'claim_type': CivicNews.CLAIM_VERIFIED,
            'status': CivicNews.STATUS_PUBLISHED,
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'source_name' in response.data

    def test_editor_can_publish_labelled_item(self, api_client, org, editor_user):
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        response = api_client.post('/api/news/', {
            'title': 'How to read a gazette',
            'body': 'An educational explainer of official notices.',
            'topic': CivicNews.TOPIC_EDUCATION_UPDATE,
            'claim_type': CivicNews.CLAIM_EDUCATIONAL,
            'status': CivicNews.STATUS_PUBLISHED,
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['claim_type'] == 'educational'
        assert response.data['status'] == 'published'
        assert response.data['published_at'] is not None

    def test_guest_cannot_see_draft_detail(self, api_client, org):
        draft = _make_news(org, title='Draft only', status=CivicNews.STATUS_DRAFT, published_at=None)
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/news/{draft.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
