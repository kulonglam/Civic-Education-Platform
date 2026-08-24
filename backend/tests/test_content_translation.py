import pytest

from apps.engagement.models import CivicNews
from apps.learning.translation import apply_record_translation
from apps.quizzes.models import Quiz
from tests.test_article_translation import PrefixProvider


@pytest.mark.django_db
class TestRecordTranslation:
    def test_quiz_english_to_arabic(self, org, editor_user):
        quiz = Quiz.objects.create(
            organization=org,
            title='Citizen rights quiz',
            description='Check your knowledge of civic rights.',
            created_by=editor_user,
        )
        provider = PrefixProvider(prefix='[ar] ')
        assert apply_record_translation(quiz, provider=provider) is True
        quiz.refresh_from_db()
        assert quiz.title_ar.startswith('[ar] ')
        assert 'Citizen rights' in quiz.title_ar

    def test_news_skips_when_arabic_present(self, org, editor_user):
        news = CivicNews.objects.create(
            organization=org,
            title='Election briefing',
            title_ar='إحاطة انتخابية',
            body='Official dates will be announced by the commission.',
            body_ar='ستعلن اللجنة المواعيد الرسمية.',
            topic='election',
            created_by=editor_user,
        )
        provider = PrefixProvider(prefix='[ar] ')
        assert apply_record_translation(news, provider=provider) is False
