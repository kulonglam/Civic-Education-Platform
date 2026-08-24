import pytest
from rest_framework import status

from apps.engagement.models import SuspiciousContentReport
from apps.learning.misinformation import AWARENESS_ARTICLES, FACT_OR_FICTION_TITLE
from apps.quizzes.models import Quiz
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestAwareness:
    def test_overview_is_public(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/awareness/')
        assert response.status_code == status.HTTP_200_OK
        keys = [row['key'] for row in response.data['lessons']]
        assert keys == ['verify', 'examples', 'social', 'credibility']

    def test_guest_can_report_suspicious_content(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post('/api/awareness/reports/', {
            'channel': 'whatsapp',
            'description': (
                'A nameless voice note claims all clinics will close tomorrow. '
                'There is no office named and people are asked to forward it.'
            ),
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'pending'
        assert SuspiciousContentReport.objects.filter(organization=org).count() == 1

    def test_report_rejects_short_description(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post('/api/awareness/reports/', {
            'channel': 'facebook',
            'description': 'Looks fake',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_guest_cannot_list_reports(self, api_client, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/awareness/reports/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_moderator_reviews_report(self, api_client, org, moderator_user):
        report = SuspiciousContentReport.objects.create(
            organization=org,
            channel='website',
            description='A page with a borrowed logo claims a new fee starts Monday without naming an office.',
        )
        bind_client_to_org(api_client, moderator_user, org, membership_role=Membership.MODERATOR)
        listing = api_client.get('/api/awareness/reports/')
        assert listing.status_code == status.HTTP_200_OK
        assert len(listing.data) == 1
        review = api_client.patch(
            f'/api/awareness/reports/{report.id}/',
            {'status': 'reviewed', 'moderator_notes': 'No matching gazette found.'},
            format='json',
        )
        assert review.status_code == status.HTTP_200_OK
        report.refresh_from_db()
        assert report.status == SuspiciousContentReport.STATUS_REVIEWED
        assert report.reviewed_by_id == moderator_user.id


@pytest.mark.django_db
def test_seed_includes_fact_or_fiction_and_awareness_articles(api_client):
    from django.core.management import call_command
    from apps.learning.models import Article

    call_command('seed_data')
    assert Quiz.objects.filter(
        organization__slug='platform-demo',
        title=FACT_OR_FICTION_TITLE,
        kind='practice',
    ).exists()
    for spec in AWARENESS_ARTICLES:
        assert Article.objects.filter(
            organization__slug='platform-demo',
            title=spec['title'],
            status='published',
        ).exists()
    api_client.credentials(HTTP_X_ORGANIZATION_SLUG='platform-demo')
    overview = api_client.get('/api/awareness/')
    assert overview.status_code == status.HTTP_200_OK
    assert overview.data['quiz'] is not None
    assert all(item['article_id'] for item in overview.data['lessons'])
