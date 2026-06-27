import pytest
from rest_framework import status

from apps.accounts.models import Role
from apps.quizzes.models import Question, Quiz
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestQuizzes:
    def test_quiz_attempt_and_pass(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(title='Civic Quiz', passing_score=50, organization=org)
        q = Question.objects.create(
            quiz=quiz,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            points=100,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'True'},
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['attempt']['passed'] is True
        assert response.data['certificate'] is not None

    def test_quiz_results(self, api_client, citizen_user, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/quizzes/results/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestForum:
    def test_create_topic(self, api_client, citizen_user, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post('/api/topics/', {
            'title': 'Democracy Discussion',
            'content': 'What does democracy mean to you?',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_approved'] is False

    def test_moderator_approves_topic(self, api_client, citizen_user, roles, django_user_model, org):
        role = Role.objects.get(name='moderator')
        moderator = django_user_model.objects.create_user(
            email='mod@test.com',
            password='TestPass123!',
            first_name='Mod',
            last_name='User',
            role=role,
        )
        bind_client_to_org(api_client, citizen_user, org)
        create_resp = api_client.post('/api/topics/', {
            'title': 'Test Topic',
            'content': 'Content',
        }, format='json')
        topic_id = create_resp.data['id']
        bind_client_to_org(api_client, moderator, org)
        response = api_client.patch(f'/api/topics/{topic_id}/moderate/', {
            'is_approved': True,
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_approved'] is True


@pytest.mark.django_db
class TestAnalytics:
    def test_analytics_requires_admin(self, api_client, citizen_user, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get('/api/analytics/overview/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_analytics_overview_admin(self, api_client, admin_user, org):
        bind_client_to_org(api_client, admin_user, org)
        response = api_client.get('/api/analytics/overview/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_users' in response.data
