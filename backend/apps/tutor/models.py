import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class TutorChat(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_chats',
    )
    article = models.ForeignKey(
        'learning.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tutor_chats',
    )
    session_id = models.CharField(max_length=64, db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()
    tokens_used = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tutor_chats'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session_id']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f'{self.user_id} ({self.role})'


class TutorDailyUsage(models.Model):
    """DB-backed per-user daily message counter. Redis is used as a fast
    write-through cache; this row is the source of truth for billing/audit."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tutor_daily_usage',
    )
    date = models.DateField(default=timezone.localdate, db_index=True)
    message_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'tutor_daily_usage'
        unique_together = [('user', 'date')]

    def __str__(self):
        return f'{self.user_id} – {self.date}: {self.message_count}'
