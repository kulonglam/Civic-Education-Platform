from django.urls import path

from .views import (
    AnalyticsForumView,
    AnalyticsLearningView,
    AnalyticsOverviewView,
    AnalyticsQuizzesView,
    ExportProgressCSVView,
    MemberProgressView,
    OrgDashboardView,
)

urlpatterns = [
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('quizzes/', AnalyticsQuizzesView.as_view(), name='analytics-quizzes'),
    path('forum/', AnalyticsForumView.as_view(), name='analytics-forum'),
    path('learning/', AnalyticsLearningView.as_view(), name='analytics-learning'),
    path('dashboard/', OrgDashboardView.as_view(), name='analytics-dashboard'),
    path('progress/', MemberProgressView.as_view(), name='analytics-progress'),
    path('export/csv/', ExportProgressCSVView.as_view(), name='analytics-export-csv'),
]
