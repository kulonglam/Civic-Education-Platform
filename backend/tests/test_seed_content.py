import pytest
from django.core.management import call_command
from rest_framework import status

from apps.accounts.management.commands.seed_data import resolve_constitution_attachment
from apps.engagement.models import CivicEvent, CivicNews, Poll
from apps.forum.models import DiscussionTopic
from apps.learning.curriculum import CATEGORY_SLUGS
from apps.learning.curriculum_lessons import LESSONS
from apps.learning.models import Article
from apps.quizzes.models import Quiz


def test_lesson_slugs_match_curriculum():
    assert [lesson['slug'] for lesson in LESSONS] == list(CATEGORY_SLUGS)


@pytest.mark.django_db
class TestSeedDataContent:
    def test_seed_creates_demo_content(self):
        call_command('seed_data')
        assert Article.objects.filter(organization__slug='platform-demo', status='published').count() >= 15
        assert Quiz.objects.filter(organization__slug='platform-demo', is_active=True).exists()
        assert DiscussionTopic.objects.filter(
            organization__slug='platform-demo',
            is_approved=True,
        ).count() >= 2
        assert DiscussionTopic.objects.filter(
            organization__slug='platform-demo',
            kind='question',
            is_approved=True,
        ).exists()
        assert Poll.objects.filter(organization__slug='platform-demo', status='open').count() >= 4
        news = CivicNews.objects.filter(organization__slug='platform-demo', status='published')
        assert news.count() >= 6
        assert news.values_list('claim_type', flat=True).distinct().count() == 4
        assert news.values_list('topic', flat=True).distinct().count() == 5
        events = CivicEvent.objects.filter(organization__slug='platform-demo', status='published')
        assert events.count() >= 6
        assert events.values_list('kind', flat=True).distinct().count() == 6

    def test_seed_is_idempotent(self):
        call_command('seed_data')
        article_count = Article.objects.filter(organization__slug='platform-demo').count()
        quiz_count = Quiz.objects.filter(organization__slug='platform-demo').count()
        news_count = CivicNews.objects.filter(organization__slug='platform-demo').count()
        event_count = CivicEvent.objects.filter(organization__slug='platform-demo').count()
        topic_count = DiscussionTopic.objects.filter(organization__slug='platform-demo').count()
        call_command('seed_data')
        assert Article.objects.filter(organization__slug='platform-demo').count() == article_count
        assert Quiz.objects.filter(organization__slug='platform-demo').count() == quiz_count
        assert CivicNews.objects.filter(organization__slug='platform-demo').count() == news_count
        assert CivicEvent.objects.filter(organization__slug='platform-demo').count() == event_count
        assert DiscussionTopic.objects.filter(organization__slug='platform-demo').count() == topic_count

    def test_seeded_articles_are_public(self, api_client):
        call_command('seed_data')
        response = api_client.get(
            '/api/articles/',
            HTTP_X_ORGANIZATION_SLUG='platform-demo',
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 10

    def test_seed_constitution_article_has_pdf_attachment(self):
        call_command('seed_data')
        constitution_entry = next(
            lesson for lesson in LESSONS if lesson['title'] == 'Understanding the Transitional Constitution'
        )
        _, expected_name = resolve_constitution_attachment(constitution_entry)
        article = Article.objects.get(
            organization__slug='platform-demo',
            title='Understanding the Transitional Constitution',
        )
        assert article.attachment_url.startswith('http')
        assert article.attachment_name == expected_name

    def test_seed_creates_full_curriculum_packs(self):
        call_command('seed_data')
        articles = Article.objects.filter(organization__slug='platform-demo', status='published')
        assert articles.count() >= len(CATEGORY_SLUGS)
        lesson_by_slug = {lesson['slug']: lesson for lesson in LESSONS}
        for slug in CATEGORY_SLUGS:
            lesson = lesson_by_slug[slug]
            article = articles.filter(category__slug=slug, title=lesson['title']).first()
            assert article is not None, f'missing published lesson for {slug}'
            assert article.attachment_url, f'{slug} missing PDF handout'
            assert article.audio_media_id, f'{slug} missing audio'
            assert article.video_media_id, f'{slug} missing video'
            assert article.featured_image_url, f'{slug} missing infographic'
