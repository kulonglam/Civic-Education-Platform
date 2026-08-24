import uuid

from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('user_registered', 'User Registered'),
        ('user_login', 'User Login'),
        ('user_logout', 'User Logout'),
        ('user_login_failed', 'User Login Failed'),
        ('email_verified', 'Email Verified'),
        ('phone_verified', 'Phone Verified'),
        ('password_reset', 'Password Reset'),
        ('user_suspended', 'User Suspended'),
        ('user_unsuspended', 'User Unsuspended'),
        ('user_role_changed', 'User Role Changed'),
        ('user_deactivated', 'User Deactivated'),
        ('data_exported', 'Data Exported'),
        ('member_invited', 'Member Invited'),
        ('member_removed', 'Member Removed'),
        ('member_role_changed', 'Member Role Changed'),
        ('org_settings_changed', 'Organization Settings Changed'),
        ('sso_configured', 'SSO Configured'),
        ('sso_login', 'SSO Login'),
        ('bulk_import', 'Bulk Import'),
        ('article_created', 'Article Created'),
        ('article_updated', 'Article Updated'),
        ('article_deleted', 'Article Deleted'),
        ('article_submitted', 'Article Submitted for Review'),
        ('article_approved', 'Article Approved'),
        ('article_rejected', 'Article Rejected'),
        ('quiz_created', 'Quiz Created'),
        ('quiz_attempt', 'Quiz Attempt'),
        ('certificate_issued', 'Certificate Issued'),
        ('topic_created', 'Topic Created'),
        ('comment_created', 'Comment Created'),
        ('content_moderated', 'Content Moderated'),
        ('admin_action', 'Admin Action'),
        ('org_activated', 'Organization Activated'),
        ('org_deactivated', 'Organization Deactivated'),
        ('password_changed', 'Password Changed'),
        ('session_revoked', 'Session Revoked'),
        ('scim_user_provisioned', 'SCIM User Provisioned'),
        ('scim_user_updated', 'SCIM User Updated'),
        ('scim_user_deactivated', 'SCIM User Deactivated'),
        ('support_case_opened', 'Support Case Opened'),
        ('support_case_updated', 'Support Case Updated'),
        ('compliance_pack_exported', 'Compliance Pack Exported'),
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
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    prev_hash = models.CharField(max_length=64, blank=True, default='')
    integrity_hash = models.CharField(max_length=64, blank=True, default='', db_index=True)

    class Meta:
        db_table = 'activity_logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.activity_type} at {self.timestamp}'
