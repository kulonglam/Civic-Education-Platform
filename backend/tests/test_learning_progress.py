import pytest
from django.utils import timezone
from rest_framework import status

from apps.learning.models import Article, ArticleProgress, MediaAsset, MediaProgress
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


@pytest.fixture
def published_article(db, org, category, citizen_user):
    return Article.objects.create(
        organization=org,
        title='Civic Rights Overview',
        content='A long article about civic rights and participation in South Sudan.',
        category=category,
        author=citizen_user,
        status='published',
        published_at=timezone.now(),
    )


@pytest.fixture
def published_media(db, org, category, citizen_user):
    return MediaAsset.objects.create(
        organization=org,
        title='Elections Explainer',
        description='How elections work.',
        media_type=MediaAsset.TYPE_VIDEO,
        source=MediaAsset.SOURCE_EXTERNAL,
        external_url='https://example.com/video.mp4',
        category=category,
        author=citizen_user,
        status='published',
        published_at=timezone.now(),
    )


@pytest.mark.django_db
class TestLearningProgress:
    def test_article_progress_requires_auth(self, api_client, org, published_article):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post(
            f'/api/articles/{published_article.id}/progress/',
            {'progress_percent': 50},
            format='json',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_record_article_progress(self, api_client, org, citizen_user, published_article):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.post(
            f'/api/articles/{published_article.id}/progress/',
            {'progress_percent': 45},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['progress_percent'] == 45
        assert response.data['completed'] is False

        complete = api_client.post(
            f'/api/articles/{published_article.id}/progress/',
            {'progress_percent': 92},
            format='json',
        )
        assert complete.status_code == status.HTTP_200_OK
        assert complete.data['completed'] is True
        assert ArticleProgress.objects.filter(user=citizen_user, completed=True).count() == 1

    def test_record_media_progress(self, api_client, org, citizen_user, published_media):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.post(
            f'/api/media/{published_media.id}/progress/',
            {'completed': True},
            format='json',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['completed'] is True
        assert MediaProgress.objects.filter(user=citizen_user, completed=True).count() == 1

    def test_my_learning_summary(self, api_client, org, citizen_user, published_article, published_media):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        api_client.post(
            f'/api/articles/{published_article.id}/progress/',
            {'progress_percent': 100, 'completed': True},
            format='json',
        )
        api_client.post(
            f'/api/media/{published_media.id}/progress/',
            {'completed': True},
            format='json',
        )

        response = api_client.get('/api/analytics/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['articles_completed'] == 1
        assert response.data['media_completed'] == 1
        assert len(response.data['by_category']) >= 1
        assert len(response.data['recent_activity']) >= 1
