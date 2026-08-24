from django.urls import path

from apps.engagement.awareness_views import (
    AwarenessOverviewView,
    SuspiciousReportListCreateView,
    SuspiciousReportReviewView,
)

urlpatterns = [
    path('', AwarenessOverviewView.as_view(), name='awareness-overview'),
    path('reports/', SuspiciousReportListCreateView.as_view(), name='awareness-reports'),
    path(
        'reports/<uuid:report_id>/',
        SuspiciousReportReviewView.as_view(),
        name='awareness-report-review',
    ),
]
