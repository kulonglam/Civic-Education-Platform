from django.urls import path

from .views import (
    AnalyticsForumView,
    AnalyticsLearningView,
    AnalyticsOverviewView,
    AnalyticsPollsView,
    AnalyticsQuizzesView,
    ExportProgressCSVView,
    InstitutionalReportPDFView,
    MemberProgressView,
    MyLearningView,
    OrgDashboardView,
)

urlpatterns = [
    path('overview/', AnalyticsOverviewView.as_view(), name='analytics-overview'),
    path('quizzes/', AnalyticsQuizzesView.as_view(), name='analytics-quizzes'),
    path('forum/', AnalyticsForumView.as_view(), name='analytics-forum'),
    path('polls/', AnalyticsPollsView.as_view(), name='analytics-polls'),
    path('learning/', AnalyticsLearningView.as_view(), name='analytics-learning'),
    path('me/', MyLearningView.as_view(), name='analytics-me'),
    path('dashboard/', OrgDashboardView.as_view(), name='analytics-dashboard'),
    path('progress/', MemberProgressView.as_view(), name='analytics-progress'),
    path('export/csv/', ExportProgressCSVView.as_view(), name='analytics-export-csv'),
    path('export/report.pdf/', InstitutionalReportPDFView.as_view(), name='analytics-export-report-pdf'),
]
