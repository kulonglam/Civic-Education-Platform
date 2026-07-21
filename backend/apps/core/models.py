import uuid

from django.conf import settings
from django.db import models


class SecurityEvent(models.Model):
    """Persisted security events for platform-admin monitoring dashboards."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=64, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='security_events',
    )
    user_email = models.EmailField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=512, blank=True)
    method = models.CharField(max_length=10, blank=True)
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.event_type} @ {self.created_at}'
