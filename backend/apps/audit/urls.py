from django.urls import path

from .views import ActivityLogExportView, ActivityLogListView

urlpatterns = [
    path('logs/', ActivityLogListView.as_view(), name='audit-logs'),
    path('logs/export/', ActivityLogExportView.as_view(), name='audit-logs-export'),
]
