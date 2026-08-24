from django.urls import path

from .sms_views import (
    BroadcastSmsView,
    PlatformBroadcastSmsView,
    SendSmsView,
    SmsHistoryView,
)
from .whatsapp_views import (
    BroadcastWhatsAppView,
    PlatformBroadcastWhatsAppView,
    SendWhatsAppView,
    WhatsAppHistoryView,
    WhatsAppStatusView,
    WhatsAppWebhookView,
)

urlpatterns = [
    path('sms/', SendSmsView.as_view(), name='notify-sms'),
    path('broadcast/', BroadcastSmsView.as_view(), name='notify-broadcast'),
    path('broadcast/platform/', PlatformBroadcastSmsView.as_view(), name='notify-platform-broadcast'),
    path('history/', SmsHistoryView.as_view(), name='notify-history'),
    path('whatsapp/', SendWhatsAppView.as_view(), name='notify-whatsapp'),
    path('whatsapp/status/', WhatsAppStatusView.as_view(), name='notify-whatsapp-status'),
    path('whatsapp/broadcast/', BroadcastWhatsAppView.as_view(), name='notify-whatsapp-broadcast'),
    path('whatsapp/broadcast/platform/', PlatformBroadcastWhatsAppView.as_view(), name='notify-whatsapp-platform-broadcast'),
    path('whatsapp/history/', WhatsAppHistoryView.as_view(), name='notify-whatsapp-history'),
    path('whatsapp/webhook/', WhatsAppWebhookView.as_view(), name='notify-whatsapp-webhook'),
]
