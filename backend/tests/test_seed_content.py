import pytest
from django.core.management import call_command
from rest_framework import status

from apps.forum.models import DiscussionTopic
from apps.learning.models import Article
from apps.quizzes.models import Quiz


@pytest.mark.django_db
class TestSeedDataContent:
    def test_seed_creates_demo_content(self):
        call_command('seed_data')
        assert Article.objects.filter(organization__slug='platform-demo', status='published').count() >= 3
        assert Quiz.objects.filter(organization__slug='platform-demo', is_active=True).exists()
        assert DiscussionTopic.objects.filter(organization__slug='platform-demo', is_approved=True).exists()

    def test_seed_is_idempotent(self):
        call_command('seed_data')
        article_count = Article.objects.filter(organization__slug='platform-demo').count()
        quiz_count = Quiz.objects.filter(organization__slug='platform-demo').count()
        call_command('seed_data')
        assert Article.objects.filter(organization__slug='platform-demo').count() == article_count
        assert Quiz.objects.filter(organization__slug='platform-demo').count() == quiz_count

    def test_seeded_articles_are_public(self, api_client):
        call_command('seed_data')
        response = api_client.get(
            '/api/articles/',
            HTTP_X_ORGANIZATION_SLUG='platform-demo',
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 3

    def test_seed_constitution_article_has_pdf_attachment(self):
        call_command('seed_data')
        article = Article.objects.get(
            organization__slug='platform-demo',
            title='Understanding the Transitional Constitution',
        )
        assert article.attachment_url.startswith('http')
        assert article.attachment_name == 'Transitional Constitution (Sample).pdf'
