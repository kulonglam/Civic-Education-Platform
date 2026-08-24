import pytest
from rest_framework import status

from apps.learning.models import Article, Category
from apps.quizzes.models import Quiz


@pytest.fixture
def bilingual_article(db, editor_user, org):
    category = Category.objects.create(organization=org, name='Constitution', slug='constitution')
    return Article.objects.create(
        title='The Constitution',
        title_ar='الدستور',
        content='English body',
        content_ar='النص العربي',
        category=category,
        author=editor_user,
        organization=org,
        status='published',
    )


@pytest.mark.django_db
class TestArticleI18n:
    def test_default_returns_english(self, api_client, bilingual_article, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/articles/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == 'The Constitution'

    def test_lang_query_param_returns_arabic(self, api_client, bilingual_article, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/articles/?lang=ar')
        assert response.status_code == status.HTTP_200_OK
        result = response.data['results'][0]
        assert result['title'] == 'الدستور'
        assert result['content'] == 'النص العربي'

    def test_accept_language_header_returns_arabic(self, api_client, bilingual_article, org):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/articles/', HTTP_ACCEPT_LANGUAGE='ar')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['title'] == 'الدستور'

    def test_missing_arabic_falls_back_to_english(self, api_client, editor_user, org):
        category = Category.objects.create(organization=org, name='Rights', slug='rights')
        Article.objects.create(
            title='English Only',
            content='Body',
            category=category,
            author=editor_user,
            organization=org,
            status='published',
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/articles/?lang=ar')
        assert response.data['results'][0]['title'] == 'English Only'


from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestQuizI18n:
    def test_quiz_title_resolves_arabic(self, api_client, citizen_user, org):
        Quiz.objects.create(
            title='Civic Quiz', title_ar='اختبار مدني', passing_score=50, organization=org,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/quizzes/?lang=ar')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        assert any(item['title'] == 'اختبار مدني' for item in results)

    def test_attempt_list_quiz_title_resolves_arabic(self, api_client, citizen_user, org):
        from apps.quizzes.models import QuizAttempt

        quiz = Quiz.objects.create(
            title='Civic Quiz',
            title_ar='اختبار مدني',
            passing_score=50,
            organization=org,
        )
        QuizAttempt.objects.create(
            quiz=quiz,
            user=citizen_user,
            organization=org,
            score=80,
            max_score=100,
            passed=True,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/quizzes/results/', HTTP_ACCEPT_LANGUAGE='ar')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'][0]['quiz_title'] == 'اختبار مدني'


@pytest.mark.django_db
class TestQuizOptionsI18n:
    def test_mcq_options_ar_exposed_for_frontend(self, api_client, citizen_user, org):
        from apps.quizzes.models import Question, Quiz

        quiz = Quiz.objects.create(title='Options Quiz', organization=org)
        Question.objects.create(
            quiz=quiz,
            question_text='Pick one',
            question_text_ar='اختر واحداً',
            question_type=Question.MCQ,
            options=['Alpha', 'Beta'],
            options_ar=['ألفا', 'بيتا'],
            correct_answer='Alpha',
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get(f'/api/quizzes/{quiz.id}/', HTTP_ACCEPT_LANGUAGE='ar')
        assert response.status_code == status.HTTP_200_OK
        question = response.data['questions'][0]
        assert question['options'] == ['Alpha', 'Beta']
        assert question['options_ar'] == ['ألفا', 'بيتا']
        assert question['question_text'] == 'اختر واحداً'
        assert 'correct_answer' not in question
        assert 'explanation' not in question
