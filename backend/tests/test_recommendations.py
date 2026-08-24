import pytest
from django.utils import timezone
from rest_framework import status

from apps.learning.models import Article, ArticleProgress
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestRecommendations:
    def test_anonymous_gets_popular_articles(self, api_client, org, category, citizen_user):
        Article.objects.create(
            organization=org,
            title='Published lesson',
            content='Body',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['personalized'] is False
        titles = [row['title'] for row in response.data['items']]
        assert 'Published lesson' in titles

    def test_in_progress_ranks_high(self, api_client, org, category, citizen_user):
        article = Article.objects.create(
            organization=org,
            title='Continue this lesson',
            content='Body',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        Article.objects.create(
            organization=org,
            title='Other lesson',
            content='Body',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
        )
        ArticleProgress.objects.create(
            organization=org,
            user=citizen_user,
            article=article,
            progress_percent=40,
            completed=False,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['personalized'] is True
        assert response.data['items'][0]['title'] == 'Continue this lesson'
        assert response.data['items'][0]['reason'] == 'in_progress'
