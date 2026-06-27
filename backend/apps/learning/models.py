import uuid

from django.conf import settings
from django.db import models

from apps.tenants.models import TenantModel


class Category(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    name_ar = models.CharField(max_length=100, blank=True)
    description_ar = models.TextField(blank=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = [('organization', 'slug'), ('organization', 'name')]

    def __str__(self):
        return self.name


class Article(TenantModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    content = models.TextField()
    content_ar = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='articles')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
    )
    tags = models.JSONField(default=list, blank=True)
    featured_image_url = models.URLField(blank=True)
    attachment_url = models.CharField(max_length=2048, blank=True, default='')
    attachment_name = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title
