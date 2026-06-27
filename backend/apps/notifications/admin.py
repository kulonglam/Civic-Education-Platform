from django.contrib import admin

from .models import Notification, SmsMessage, WebPushSubscription

admin.site.register(Notification)


@admin.register(SmsMessage)
class SmsMessageAdmin(admin.ModelAdmin):
    list_display = ('phone', 'message_type', 'status', 'user', 'sent_at', 'created_at')
    list_filter = ('status', 'message_type', 'created_at')
    search_fields = ('phone', 'message', 'user__email')
    readonly_fields = ('id', 'created_at', 'sent_at')


@admin.register(WebPushSubscription)
class WebPushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'endpoint_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'endpoint')
    readonly_fields = ('id', 'created_at', 'p256dh', 'auth')

    @admin.display(description='Endpoint')
    def endpoint_preview(self, obj):
        return obj.endpoint[:80] + ('…' if len(obj.endpoint) > 80 else '')
