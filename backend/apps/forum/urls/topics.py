from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import (
    DiscussionTopicViewSet,
    PendingModerationView,
    ForumReportReviewView,
    TopicAcceptAnswerView,
    TopicCommentCreateView,
    TopicLockView,
    TopicModerateView,
    TopicReportView,
)

router = DefaultRouter()
router.register('', DiscussionTopicViewSet, basename='topic')

urlpatterns = [
    path('pending/', PendingModerationView.as_view(), name='pending-moderation'),
    path('reports/<uuid:id>/', ForumReportReviewView.as_view(), name='forum-report-review'),
    path('<uuid:id>/comments/', TopicCommentCreateView.as_view(), name='topic-comments'),
    path('<uuid:id>/moderate/', TopicModerateView.as_view(), name='topic-moderate'),
    path('<uuid:id>/lock/', TopicLockView.as_view(), name='topic-lock'),
    path('<uuid:id>/accept-answer/', TopicAcceptAnswerView.as_view(), name='topic-accept-answer'),
    path('<uuid:id>/report/', TopicReportView.as_view(), name='topic-report'),
    path('', include(router.urls)),
]
