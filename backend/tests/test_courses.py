import pytest
from rest_framework import status

from apps.learning.models import Article, ArticleProgress, Course, CourseLesson
from apps.tenants.models import Membership
from tests.conftest import bind_client_to_org


def _published_article(org, category, author, title='Rights in the constitution'):
    return Article.objects.create(
        organization=org,
        category=category,
        author=author,
        title=title,
        content='Citizens have rights protected by the constitution.',
        status='published',
    )


@pytest.mark.django_db
class TestCourses:
    def test_public_list_hides_drafts(self, api_client, org, category, editor_user):
        article = _published_article(org, category, editor_user)
        published = Course.objects.create(
            organization=org,
            title='Constitution path',
            slug='constitution-path',
            description='Start with rights.',
            status=Course.STATUS_PUBLISHED,
            created_by=editor_user,
        )
        CourseLesson.objects.create(
            organization=org, course=published, article=article, sort_order=0,
        )
        Course.objects.create(
            organization=org,
            title='Hidden draft',
            slug='hidden-draft',
            status=Course.STATUS_DRAFT,
            created_by=editor_user,
        )
        response = api_client.get('/api/courses/')
        assert response.status_code == status.HTTP_200_OK
        titles = [row['title'] for row in response.data['results']]
        assert 'Constitution path' in titles
        assert 'Hidden draft' not in titles

    def test_detail_includes_progress(self, api_client, org, category, editor_user, citizen_user):
        first = _published_article(org, category, editor_user, 'Lesson one')
        second = _published_article(org, category, editor_user, 'Lesson two')
        course = Course.objects.create(
            organization=org,
            title='Civic path',
            slug='civic-path',
            status=Course.STATUS_PUBLISHED,
            created_by=editor_user,
        )
        CourseLesson.objects.create(organization=org, course=course, article=first, sort_order=0)
        CourseLesson.objects.create(organization=org, course=course, article=second, sort_order=1)
        ArticleProgress.objects.create(
            organization=org, user=citizen_user, article=first, completed=True, progress_percent=100,
        )
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        response = api_client.get(f'/api/courses/{course.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['lesson_count'] == 2
        assert response.data['completed_count'] == 1
        assert response.data['lessons'][0]['completed'] is True
        assert response.data['lessons'][1]['completed'] is False

    def test_editor_can_create_course(self, api_client, org, category, editor_user):
        article = _published_article(org, category, editor_user)
        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.CONTENT_MANAGER)
        response = api_client.post(
            '/api/courses/',
            {
                'title': 'Peacebuilding path',
                'slug': 'peacebuilding-path',
                'description': 'Ordered lessons on peace.',
                'status': 'published',
                'lesson_ids': [str(article.id)],
            },
            format='json',
        )
        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data['lesson_count'] == 1
        assert response.data['lessons'][0]['article_id'] == str(article.id)
