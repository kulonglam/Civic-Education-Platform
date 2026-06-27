import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel


class DiscussionTopic(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discussion_topics',
    )
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'discussion_topics'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class DiscussionComment(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(
        DiscussionTopic,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discussion_comments',
    )
    comment = models.TextField()
    is_approved = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discussion_comments'
        ordering = ['created_at']

    def __str__(self):
        return self.comment[:50]
