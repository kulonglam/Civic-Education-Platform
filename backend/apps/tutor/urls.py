from django.urls import path

from .views import (
    ChatHistoryDetailView,
    ChatHistoryListView,
    ChatStreamView,
    ChatView,
    SessionView,
    TutorAdminUsageView,
    TutorUsageView,
)

urlpatterns = [
    path('chat/', ChatView.as_view(), name='tutor-chat'),
    path('chat/stream/', ChatStreamView.as_view(), name='tutor-chat-stream'),
    path('chat/session/', SessionView.as_view(), name='tutor-session'),
    path('chat/history/', ChatHistoryListView.as_view(), name='tutor-chat-history'),
    path('chat/history/<str:session_id>/', ChatHistoryDetailView.as_view(), name='tutor-chat-history-detail'),
    path('usage/', TutorUsageView.as_view(), name='tutor-usage'),
    path('usage/platform/', TutorAdminUsageView.as_view(), name='tutor-admin-usage'),
]
