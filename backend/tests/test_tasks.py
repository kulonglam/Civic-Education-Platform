from unittest.mock import patch

import pytest
from django.core import mail
from rest_framework import status

from apps.core.tasks import send_email_task
from apps.notifications.models import Notification
from apps.notifications.tasks import broadcast_notification_task
from apps.quizzes.models import Certificate, Question, Quiz
from tests.conftest import bind_client_to_org


@pytest.mark.django_db
class TestEmailTask:
    def test_send_email_task_delivers(self, db):
        send_email_task.delay('Subject', 'Body', ['someone@test.com'])
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Subject'
        assert mail.outbox[0].to == ['someone@test.com']


@pytest.mark.django_db
class TestBroadcastTask:
    def test_broadcast_creates_notification_for_each_active_user(
        self, citizen_user, editor_user, admin_user
    ):
        count = broadcast_notification_task('announcement', 'Hello', 'New content is live')
        assert count == 3
        for user in (citizen_user, editor_user, admin_user):
            assert Notification.objects.filter(
                user=user, notification_type='announcement'
            ).count() == 1

    def test_broadcast_skips_inactive_users(self, citizen_user, editor_user):
        editor_user.is_active = False
        editor_user.save(update_fields=['is_active'])

        count = broadcast_notification_task('announcement', 'Hi', 'msg')
        assert count == 1
        assert not Notification.objects.filter(user=editor_user).exists()


@pytest.mark.django_db
class TestArticlePublishBroadcast:
    def test_publishing_article_notifies_all_users(self, api_client, editor_user, citizen_user, org):
        from apps.learning.models import Article, Category

        category = Category.objects.create(organization=org, name='Rights', slug='rights')
        Article.objects.create(
            title='Know Your Rights',
            content='Body',
            category=category,
            author=editor_user,
            organization=org,
            status='published',
        )
        # notify_all_users enqueues broadcast_notification_task (eager in tests).
        assert Notification.objects.filter(user=citizen_user).exists()


@pytest.mark.django_db
class TestCertificateTask:
    def test_certificate_pdf_generated_on_pass(self, api_client, citizen_user, org):
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

        fake_url = 'https://storage.test/certificates/cert.pdf'
        with patch('apps.quizzes.services.upload_bytesio', return_value=fake_url):
            response = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
                'answers': {str(q.id): 'True'},
            }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['attempt']['passed'] is True
        certificate = Certificate.objects.get(user=citizen_user, quiz=quiz)
        # PDF task runs eagerly during the request and stores the upload URL.
        certificate.refresh_from_db()
        assert certificate.pdf_url == fake_url

    def test_no_certificate_on_fail(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(title='Hard Quiz', passing_score=80, organization=org)
        q = Question.objects.create(
            quiz=quiz,
            question_text='Trick question?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            points=100,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'False'},
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['attempt']['passed'] is False
        assert response.data['certificate'] is None
        assert not Certificate.objects.filter(user=citizen_user, quiz=quiz).exists()
