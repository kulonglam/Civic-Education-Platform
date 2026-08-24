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
        review = response.data['review']
        assert len(review) == 1
        assert review[0]['is_correct'] is True
        assert review[0]['correct_answer'] == 'True'

    def test_learner_retrieve_hides_answers_and_explanations(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(title='Hidden keys', passing_score=50, organization=org)
        Question.objects.create(
            quiz=quiz,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            explanation='Because citizens share public power.',
            points=1,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.get(f'/api/quizzes/{quiz.id}/')
        assert response.status_code == status.HTTP_200_OK
        question = response.data['questions'][0]
        assert 'correct_answer' not in question
        assert 'explanation' not in question
        assert 'option_feedback' not in question

    def test_practice_pass_does_not_issue_certificate(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(
            title='Practice drill',
            passing_score=50,
            organization=org,
            kind=Quiz.KIND_PRACTICE,
        )
        q = Question.objects.create(
            quiz=quiz,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            explanation='Voting is a civic duty.',
            points=100,
        )
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'True'},
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['attempt']['passed'] is True
        assert response.data['certificate'] is None
        assert response.data['review'][0]['explanation'] == 'Voting is a civic duty.'

    def test_check_answer_only_for_per_question_practice(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(
            title='Instant practice',
            passing_score=50,
            organization=org,
            kind=Quiz.KIND_PRACTICE,
            feedback_mode=Quiz.FEEDBACK_PER_QUESTION,
        )
        q = Question.objects.create(
            quiz=quiz,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            explanation='Yes — peaceful participation is a duty.',
            points=1,
        )
        bind_client_to_org(api_client, citizen_user, org)
        ok = api_client.post(f'/api/quizzes/{quiz.id}/check-answer/', {
            'question_id': str(q.id),
            'answer': 'False',
        }, format='json')
        assert ok.status_code == status.HTTP_200_OK
        assert ok.data['is_correct'] is False
        assert ok.data['correct_answer'] == 'True'
        assert 'duty' in ok.data['explanation']

        assessment = Quiz.objects.create(
            title='Final exam',
            passing_score=50,
            organization=org,
            kind=Quiz.KIND_ASSESSMENT,
            feedback_mode=Quiz.FEEDBACK_END,
        )
        aq = Question.objects.create(
            quiz=assessment,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            points=1,
        )
        blocked = api_client.post(f'/api/quizzes/{assessment.id}/check-answer/', {
            'question_id': str(aq.id),
            'answer': 'True',
        }, format='json')
        assert blocked.status_code == status.HTTP_400_BAD_REQUEST

    def test_max_attempts_blocks_extra_submits(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(
            title='Limited attempts',
            passing_score=80,
            organization=org,
            max_attempts=1,
        )
        q = Question.objects.create(
            quiz=quiz,
            question_text='Is voting a civic duty?',
            question_type='true_false',
            options=['True', 'False'],
            correct_answer='True',
            points=100,
        )
        bind_client_to_org(api_client, citizen_user, org)
        first = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'False'},
        }, format='json')
        assert first.status_code == status.HTTP_200_OK
        second = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'True'},
        }, format='json')
        assert second.status_code == status.HTTP_403_FORBIDDEN

    def test_scenario_teaches_from_the_chosen_option(self, api_client, citizen_user, org):
        quiz = Quiz.objects.create(
            title='Civic choices',
            passing_score=50,
            organization=org,
            kind=Quiz.KIND_PRACTICE,
            feedback_mode=Quiz.FEEDBACK_PER_QUESTION,
        )
        q = Question.objects.create(
            quiz=quiz,
            question_text='You witness an unofficial fee. What do you do?',
            question_type=Question.SCENARIO,
            options=['Report through official channels', 'Stay silent'],
            correct_answer='Report through official channels',
            option_feedback=[
                {'en': 'Reporting is peaceful civic duty and follows legal process.', 'ar': ''},
                {'en': 'Silence leaves the citizen unprotected.', 'ar': ''},
            ],
            points=1,
        )
        bind_client_to_org(api_client, citizen_user, org)
        checked = api_client.post(f'/api/quizzes/{quiz.id}/check-answer/', {
            'question_id': str(q.id),
            'answer': 'Stay silent',
        }, format='json')
        assert checked.status_code == status.HTTP_200_OK
        assert checked.data['is_correct'] is False
        assert 'unprotected' in checked.data['explanation']

        submitted = api_client.post(f'/api/quizzes/{quiz.id}/attempt/', {
            'answers': {str(q.id): 'Stay silent'},
        }, format='json')
        assert submitted.status_code == status.HTTP_200_OK
        assert submitted.data['certificate'] is None
        assert 'unprotected' in submitted.data['review'][0]['explanation']

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

    def test_citizen_question_stays_in_queue(self, api_client, citizen_user, org):
        bind_client_to_org(api_client, citizen_user, org)
        response = api_client.post('/api/topics/', {
            'title': 'How do I verify a polling rumour?',
            'content': 'What official source should I check first?',
            'kind': 'question',
            'board': 'elections',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['is_approved'] is False
        assert response.data['kind'] == 'question'
        assert response.data['board'] == 'elections'

    def test_public_list_filters_questions(self, api_client, citizen_user, org):
        from apps.forum.models import DiscussionTopic

        DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='Open discussion',
            content='Talk about county meetings.',
            kind=DiscussionTopic.KIND_DISCUSSION,
            board='governance',
            is_approved=True,
        )
        question = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='What is a peaceful rumour check?',
            content='Name one official source.',
            kind=DiscussionTopic.KIND_QUESTION,
            board='elections',
            is_approved=True,
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/topics/', {'kind': 'question'})
        assert response.status_code == status.HTTP_200_OK
        ids = [row['id'] for row in response.data['results']]
        assert str(question.id) in ids
        assert all(row['kind'] == 'question' for row in response.data['results'])

    def test_editor_reply_is_expert_and_queued(
        self, api_client, citizen_user, editor_user, org,
    ):
        from apps.forum.models import DiscussionTopic
        from apps.tenants.models import Membership

        topic = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='How should youth join a hearing?',
            content='Ask for practical steps.',
            kind=DiscussionTopic.KIND_QUESTION,
            board='governance',
            is_approved=True,
        )
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.MEMBER)
        response = api_client.post(f'/api/topics/{topic.id}/comments/', {
            'comment': 'Ask the payam administrator for the public hearing notice.',
        }, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        comment = topic.comments.get()
        assert comment.is_expert is True
        assert comment.is_approved is False

    def test_accept_answer(self, api_client, citizen_user, editor_user, org):
        from apps.forum.models import DiscussionComment, DiscussionTopic
        from apps.tenants.models import Membership

        topic = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='Where do I report a rumour?',
            content='Need a peaceful official path.',
            kind=DiscussionTopic.KIND_QUESTION,
            board='media',
            is_approved=True,
        )
        answer = DiscussionComment.objects.create(
            organization=org,
            topic=topic,
            author=editor_user,
            comment='Use the official elections office notice, not a forwarded chat.',
            is_approved=True,
            is_expert=True,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.post(f'/api/topics/{topic.id}/accept-answer/', {
            'comment_id': str(answer.id),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['accepted_answer_id'] == str(answer.id)

    def test_public_retrieve_hides_unapproved_comments(self, api_client, citizen_user, org):
        from apps.forum.models import DiscussionComment, DiscussionTopic

        topic = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='Approved thread',
            content='Visible to the public.',
            is_approved=True,
        )
        DiscussionComment.objects.create(
            organization=org,
            topic=topic,
            author=citizen_user,
            comment='This should stay in the queue.',
            is_approved=False,
        )
        DiscussionComment.objects.create(
            organization=org,
            topic=topic,
            author=citizen_user,
            comment='This approved reply is public.',
            is_approved=True,
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/topics/{topic.id}/')
        assert response.status_code == status.HTTP_200_OK
        comments = response.data['comments']
        assert len(comments) == 1
        assert comments[0]['comment'] == 'This approved reply is public.'

    def test_locked_topic_rejects_comments(self, api_client, citizen_user, moderator_user, org):
        from apps.forum.models import DiscussionTopic

        topic = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='Locked after abuse',
            content='Moderators closed this thread.',
            is_approved=True,
        )
        bind_client_to_org(api_client, moderator_user, org)
        locked = api_client.patch(f'/api/topics/{topic.id}/lock/', {
            'is_locked': True,
        }, format='json')
        assert locked.status_code == status.HTTP_200_OK
        assert locked.data['is_locked'] is True
        bind_client_to_org(api_client, citizen_user, org)
        blocked = api_client.post(f'/api/topics/{topic.id}/comments/', {
            'comment': 'Should not post on a locked thread.',
        }, format='json')
        assert blocked.status_code == status.HTTP_403_FORBIDDEN

    def test_report_hides_content_when_reviewed(
        self, api_client, citizen_user, moderator_user, django_user_model, org,
    ):
        from apps.forum.models import DiscussionTopic, ForumReport

        topic = DiscussionTopic.objects.create(
            organization=org,
            author=citizen_user,
            title='A post that needs review',
            content='Public civic thread.',
            is_approved=True,
        )
        reporter = django_user_model.objects.create_user(
            email='reporter@test.com',
            password='TestPass123!',
            first_name='Pat',
            last_name='Reporter',
        )
        bind_client_to_org(api_client, reporter, org)
        created = api_client.post(f'/api/topics/{topic.id}/report/', {
            'reason': 'misinformation',
            'details': 'The post names no office and asks people to forward a rumour.',
        }, format='json')
        assert created.status_code == status.HTTP_201_CREATED
        report_id = created.data['id']
        bind_client_to_org(api_client, moderator_user, org)
        pending = api_client.get('/api/topics/pending/')
        assert pending.status_code == status.HTTP_200_OK
        assert any(row['id'] == report_id for row in pending.data['reports'])
        reviewed = api_client.patch(f'/api/topics/reports/{report_id}/', {
            'status': 'reviewed',
            'moderator_notes': 'Hidden until a named source is added.',
        }, format='json')
        assert reviewed.status_code == status.HTTP_200_OK
        topic.refresh_from_db()
        assert topic.is_approved is False
        assert ForumReport.objects.get(id=report_id).status == ForumReport.STATUS_REVIEWED


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
        assert 'active_users_30d' in response.data
        assert 'lesson_completion_rate' in response.data
        assert 'media_completion_rate' in response.data
        assert 'member_completion_rate' in response.data

    def test_analytics_learning_insights(self, api_client, admin_user, citizen_user, org, category):
        from django.utils import timezone

        from apps.learning.models import Article, ArticleProgress

        article = Article.objects.create(
            organization=org,
            title='Popular civic lesson',
            content='Body',
            title_ar='درس مدني',
            category=category,
            author=citizen_user,
            status='published',
            published_at=timezone.now(),
            tags=['constitution'],
        )
        ArticleProgress.objects.create(
            organization=org,
            user=citizen_user,
            article=article,
            progress_percent=100,
            completed=True,
        )
        profile = citizen_user.profile
        profile.preferred_language = 'ar'
        profile.region = 'central_equatoria'
        profile.save(update_fields=['preferred_language', 'region'])

        bind_client_to_org(api_client, admin_user, org)
        response = api_client.get('/api/analytics/learning/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['completion']['lesson_completions'] == 1
        assert data['completion']['lesson_completion_rate'] == 100.0
        assert data['popular_lessons'][0]['title'] == 'Popular civic lesson'
        assert data['popular_lessons'][0]['completions'] == 1
        assert any(row['key'] == 'ar' for row in data['languages'])
        assert 'translation' in data
        assert any(row['model'] == 'learning.Article' for row in data['translation']['rows'])
