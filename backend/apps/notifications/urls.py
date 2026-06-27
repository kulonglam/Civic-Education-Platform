from django.urls import path

from .views import (
    BroadcastNotificationView,
    NotificationListView,
    NotificationReadAllView,
    NotificationReadView,
    PushSubscriptionCleanupView,
    PushSubscriptionStatsView,
    WebPushSubscribeView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('broadcast/', BroadcastNotificationView.as_view(), name='notification-broadcast'),
    path('push/subscribe/', WebPushSubscribeView.as_view(), name='push-subscribe'),
    path('push/stats/', PushSubscriptionStatsView.as_view(), name='push-stats'),
    path('push/cleanup/', PushSubscriptionCleanupView.as_view(), name='push-cleanup'),
    path('read-all/', NotificationReadAllView.as_view(), name='notification-read-all'),
    path('<uuid:id>/read/', NotificationReadView.as_view(), name='notification-read'),
]
