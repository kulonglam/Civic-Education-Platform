import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel


class Notification(TenantModel):
    TYPE_CHOICES = [
        ('new_content', 'New Content'),
        ('quiz_result', 'Quiz Result'),
        ('certificate', 'Certificate'),
        ('announcement', 'Announcement'),
        ('forum', 'Forum'),
        ('event_reminder', 'Event reminder'),
        ('event_registration', 'Event registration'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class SmsMessage(TenantModel):
    TYPE_SMS = 'sms'
    TYPE_OTP = 'otp'
    TYPE_BROADCAST = 'broadcast'
    TYPE_CHOICES = [
        (TYPE_SMS, 'SMS'),
        (TYPE_OTP, 'OTP'),
        (TYPE_BROADCAST, 'Broadcast'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_messages',
    )
    phone = models.CharField(max_length=20, db_index=True)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_SMS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider_reference = models.CharField(max_length=255, blank=True)
    error_detail = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sms_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} ({self.status})'


class NotificationPreference(models.Model):
    """Per-user, per-type channel preferences for notification fan-out."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    in_app = models.BooleanField(default=True, help_text='Show in-app notification bell')
    push = models.BooleanField(default=True, help_text='Send Web Push to subscribed devices')
    sms = models.BooleanField(default=False, help_text='Send SMS (requires Pro/Enterprise plan)')
    # Per-type overrides (null = inherit from global flag above)
    quiz_result_push = models.BooleanField(null=True, blank=True, default=None)
    certificate_push = models.BooleanField(null=True, blank=True, default=None)
    forum_push = models.BooleanField(null=True, blank=True, default=None)
    announcement_sms = models.BooleanField(null=True, blank=True, default=None)
    whatsapp = models.BooleanField(
        default=False,
        help_text='Send civic alerts on WhatsApp (same phone number as SMS).',
    )

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f'Preferences for {self.user_id}'

    def wants_push(self, notification_type: str) -> bool:
        override = {
            'quiz_result': self.quiz_result_push,
            'certificate': self.certificate_push,
            'forum': self.forum_push,
        }.get(notification_type)
        return self.push if override is None else override

    def wants_sms(self, notification_type: str) -> bool:
        override = {
            'announcement': self.announcement_sms,
        }.get(notification_type)
        return self.sms if override is None else override

    def wants_whatsapp(self, notification_type: str) -> bool:  # noqa: ARG002
        return bool(self.whatsapp)


class WhatsAppMessage(TenantModel):
    TYPE_ALERT = 'alert'
    TYPE_BROADCAST = 'broadcast'
    TYPE_INBOUND = 'inbound'
    TYPE_CHOICES = [
        (TYPE_ALERT, 'Alert'),
        (TYPE_BROADCAST, 'Broadcast'),
        (TYPE_INBOUND, 'Inbound'),
    ]

    DIRECTION_OUTBOUND = 'outbound'
    DIRECTION_INBOUND = 'inbound'
    DIRECTION_CHOICES = [
        (DIRECTION_OUTBOUND, 'Outbound'),
        (DIRECTION_INBOUND, 'Inbound'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='whatsapp_messages',
    )
    phone = models.CharField(max_length=20, db_index=True)
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_ALERT)
    direction = models.CharField(max_length=12, choices=DIRECTION_CHOICES, default=DIRECTION_OUTBOUND)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    provider_reference = models.CharField(max_length=255, blank=True)
    error_detail = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'whatsapp_messages'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.phone} ({self.status})'


class WebPushSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'web_push_subscriptions'

    def __str__(self):
        return f'Push subscription for {self.user_id}'
