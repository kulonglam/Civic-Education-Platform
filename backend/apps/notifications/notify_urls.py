from django.urls import path

from .sms_views import (
    BroadcastSmsView,
    PlatformBroadcastSmsView,
    SendSmsView,
    SmsHistoryView,
)

urlpatterns = [
    path('sms/', SendSmsView.as_view(), name='notify-sms'),
    path('broadcast/', BroadcastSmsView.as_view(), name='notify-broadcast'),
    path('broadcast/platform/', PlatformBroadcastSmsView.as_view(), name='notify-platform-broadcast'),
    path('history/', SmsHistoryView.as_view(), name='notify-history'),
]
