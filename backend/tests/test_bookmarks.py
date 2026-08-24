import pytest
from django.utils import timezone
from rest_framework import status

from apps.learning.models import Article, Bookmark, MediaAsset
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
class TestBookmarks:
    def test_toggle_requires_auth(self, api_client, org, published_article):
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.post(f'/api/articles/{published_article.id}/bookmark/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_toggle_article_bookmark(self, api_client, org, citizen_user, published_article):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        add = api_client.post(f'/api/articles/{published_article.id}/bookmark/')
        assert add.status_code == status.HTTP_200_OK
        assert add.data['bookmarked'] is True
        assert Bookmark.objects.filter(user=citizen_user, article=published_article).exists()

        detail = api_client.get(f'/api/articles/{published_article.id}/')
        assert detail.data['is_bookmarked'] is True

        remove = api_client.post(f'/api/articles/{published_article.id}/bookmark/')
        assert remove.status_code == status.HTTP_200_OK
        assert remove.data['bookmarked'] is False
        assert not Bookmark.objects.filter(user=citizen_user, article=published_article).exists()

    def test_toggle_media_bookmark(self, api_client, org, citizen_user, published_media):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        add = api_client.post(f'/api/media/{published_media.id}/bookmark/')
        assert add.status_code == status.HTTP_200_OK
        assert add.data['bookmarked'] is True

        listing = api_client.get('/api/bookmarks/')
        assert listing.status_code == status.HTTP_200_OK
        results = listing.data['results'] if isinstance(listing.data, dict) else listing.data
        assert len(results) == 1
        assert results[0]['kind'] == 'media'
        assert results[0]['media']['id'] == str(published_media.id)

        delete = api_client.delete(f'/api/bookmarks/{results[0]["id"]}/')
        assert delete.status_code == status.HTTP_204_NO_CONTENT
        assert Bookmark.objects.filter(user=citizen_user).count() == 0

    def test_cannot_bookmark_draft(self, api_client, org, citizen_user, category):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        draft = Article.objects.create(
            organization=org,
            title='Draft lesson',
            content='Not published.',
            category=category,
            author=citizen_user,
            status='draft',
        )
        response = api_client.post(f'/api/articles/{draft.id}/bookmark/')
        assert response.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
        )

    def test_list_is_scoped_to_current_user(
        self, api_client, org, citizen_user, editor_user, published_article,
    ):
        bind_client_to_org(api_client, citizen_user, org, membership_role=Membership.MEMBER)
        api_client.post(f'/api/articles/{published_article.id}/bookmark/')

        bind_client_to_org(api_client, editor_user, org, membership_role=Membership.MEMBER)
        listing = api_client.get('/api/bookmarks/')
        results = listing.data['results'] if isinstance(listing.data, dict) else listing.data
        assert results == []


@pytest.mark.django_db
class TestPublicQuizList:
    def test_anonymous_can_list_active_quizzes(self, api_client, org):
        from apps.quizzes.models import Quiz

        Quiz.objects.create(
            title='Public civic quiz',
            passing_score=70,
            organization=org,
            is_active=True,
        )
        Quiz.objects.create(
            title='Hidden draft quiz',
            passing_score=70,
            organization=org,
            is_active=False,
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get('/api/quizzes/')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if isinstance(response.data, dict) else response.data
        titles = [item['title'] for item in results]
        assert 'Public civic quiz' in titles
        assert 'Hidden draft quiz' not in titles
        assert 'questions' not in results[0]
        assert results[0]['question_count'] == 0

    def test_anonymous_cannot_retrieve_quiz(self, api_client, org):
        from apps.quizzes.models import Quiz

        quiz = Quiz.objects.create(
            title='Take me',
            passing_score=70,
            organization=org,
            is_active=True,
        )
        api_client.credentials(HTTP_X_TENANT_SLUG=org.slug)
        response = api_client.get(f'/api/quizzes/{quiz.id}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
