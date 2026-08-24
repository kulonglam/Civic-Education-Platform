import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel

from .constants import FORUM_BOARDS, REPORT_REASONS


class DiscussionTopic(TenantModel):
    KIND_DISCUSSION = 'discussion'
    KIND_QUESTION = 'question'
    KIND_CHOICES = [
        (KIND_DISCUSSION, 'Discussion'),
        (KIND_QUESTION, 'Question'),
    ]
    BOARD_CHOICES = [(slug, slug) for slug in FORUM_BOARDS]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = models.TextField()
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        default=KIND_DISCUSSION,
        db_index=True,
    )
    board = models.CharField(
        max_length=32,
        choices=BOARD_CHOICES,
        default='general',
        db_index=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='discussion_topics',
    )
    is_approved = models.BooleanField(default=False, db_index=True)
    is_locked = models.BooleanField(default=False)
    accepted_answer = models.ForeignKey(
        'DiscussionComment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
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
    is_expert = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discussion_comments'
        ordering = ['created_at']

    def __str__(self):
        return self.comment[:50]


class ForumReport(TenantModel):
    TARGET_TOPIC = 'topic'
    TARGET_COMMENT = 'comment'
    TARGET_CHOICES = [
        (TARGET_TOPIC, 'Topic'),
        (TARGET_COMMENT, 'Comment'),
    ]
    REASON_CHOICES = [(reason, reason) for reason in REPORT_REASONS]
    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_type = models.CharField(max_length=16, choices=TARGET_CHOICES, db_index=True)
    topic = models.ForeignKey(
        DiscussionTopic,
        on_delete=models.CASCADE,
        related_name='reports',
    )
    comment = models.ForeignKey(
        DiscussionComment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
    )
    reason = models.CharField(max_length=40, choices=REASON_CHOICES, db_index=True)
    details = models.TextField(blank=True, default='')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_reports',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    moderator_notes = models.TextField(blank=True, default='')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forum_reports_reviewed',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'forum_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reason} · {self.target_type}'
