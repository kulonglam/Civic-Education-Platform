from django.urls import path

from .views import ChatView, ClearSessionView, TutorAdminUsageView, TutorUsageView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='tutor-chat'),
    path('chat/session/', ClearSessionView.as_view(), name='tutor-clear-session'),
    path('usage/', TutorUsageView.as_view(), name='tutor-usage'),
    path('usage/platform/', TutorAdminUsageView.as_view(), name='tutor-admin-usage'),
]
