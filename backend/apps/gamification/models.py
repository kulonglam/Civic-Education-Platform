import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel


class Badge(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(max_length=50)
    name = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    icon = models.CharField(max_length=30, default='star')
    xp_required = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        db_table = 'badges'
        ordering = ['sort_order', 'name']
        unique_together = [('organization', 'slug')]

    def __str__(self):
        return self.name


class UserBadge(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='earned_badges',
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awards')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_badges'
        unique_together = [('organization', 'user', 'badge')]
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user_id} · {self.badge.slug}'
