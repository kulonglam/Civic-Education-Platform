from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import DiscussionTopicViewSet, PendingModerationView, TopicCommentCreateView, TopicModerateView

router = DefaultRouter()
router.register('', DiscussionTopicViewSet, basename='topic')

urlpatterns = [
    path('pending/', PendingModerationView.as_view(), name='pending-moderation'),
    path('<uuid:id>/comments/', TopicCommentCreateView.as_view(), name='topic-comments'),
    path('<uuid:id>/moderate/', TopicModerateView.as_view(), name='topic-moderate'),
    path('', include(router.urls)),
]
