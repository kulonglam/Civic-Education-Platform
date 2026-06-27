import uuid

from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('user_registered', 'User Registered'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('email_verified', 'Email Verified'),
        ('password_reset', 'Password Reset'),
        ('user_suspended', 'User Suspended'),
        ('user_unsuspended', 'User Unsuspended'),
        ('user_role_changed', 'User Role Changed'),
        ('article_created', 'Article Created'),
        ('article_updated', 'Article Updated'),
        ('article_deleted', 'Article Deleted'),
        ('quiz_created', 'Quiz Created'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('certificate_issued', 'Certificate Issued'),
        ('topic_created', 'Topic Created'),
        ('comment_created', 'Comment Created'),
        ('content_moderated', 'Content Moderated'),
        ('admin_action', 'Admin Action'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'tenants.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='activity_logs',
        db_index=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.activity_type} at {self.timestamp}'
