import uuid

from django.conf import settings
from django.db import models

from apps.core.constants import LANGUAGE_CHOICES
from apps.tenants.models import TenantModel


class Category(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    description = models.TextField(blank=True)
    name_ar = models.CharField(max_length=100, blank=True)
    description_ar = models.TextField(blank=True)
    is_locked = models.BooleanField(
        default=False,
        help_text='Official curriculum category — cannot be deleted; slug/name locked for non-owners.',
    )

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']
        unique_together = [('organization', 'slug'), ('organization', 'name')]

    def __str__(self):
        return self.name


class MediaAsset(TenantModel):
    TYPE_AUDIO = 'audio'
    TYPE_VIDEO = 'video'
    TYPE_CHOICES = [
        (TYPE_AUDIO, 'Audio'),
        (TYPE_VIDEO, 'Video'),
    ]

    SOURCE_UPLOAD = 'upload'
    SOURCE_EXTERNAL = 'external'
    SOURCE_CHOICES = [
        (SOURCE_UPLOAD, 'Upload'),
        (SOURCE_EXTERNAL, 'External URL'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    media_type = models.CharField(max_length=10, choices=TYPE_CHOICES, db_index=True)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default=SOURCE_EXTERNAL)
    file_url = models.CharField(max_length=2048, blank=True, default='')
    external_url = models.URLField(blank=True, default='')
    mime_type = models.CharField(max_length=100, blank=True, default='')
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    thumbnail_url = models.URLField(blank=True, default='')
    captions_url = models.URLField(
        blank=True,
        default='',
        help_text='WebVTT captions URL for audio/video accessibility.',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='media_assets',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='media_assets',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_assets'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return f'{self.title} ({self.media_type})'

    @property
    def playback_url(self) -> str:
        if self.source == self.SOURCE_UPLOAD:
            return (self.file_url or '').strip()
        return (self.external_url or self.file_url or '').strip()


class Article(TenantModel):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_review', 'Pending review'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    TRANSLATION_NONE = 'none'
    TRANSLATION_MACHINE = 'machine'
    TRANSLATION_FAILED = 'failed'
    TRANSLATION_STATUS_CHOICES = [
        (TRANSLATION_NONE, 'None'),
        (TRANSLATION_MACHINE, 'Machine'),
        (TRANSLATION_FAILED, 'Failed'),
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
    attachment_version = models.CharField(max_length=50, blank=True, default='')
    document_label = models.CharField(
        max_length=150,
        blank=True,
        default='',
        help_text='Institutional label for controlled documents (e.g. Transitional Constitution).',
    )
    is_controlled_document = models.BooleanField(
        default=False,
        help_text='Controlled institutional PDF — version/label required; deletion restricted.',
    )
    audio_media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles_as_audio',
    )
    video_media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles_as_video',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', db_index=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_articles',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    tutor_index_text = models.TextField(
        blank=True,
        default='',
        help_text='Pre-indexed body + PDF text for AI tutor retrieval.',
    )
    source_language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        blank=True,
        default='',
        help_text='Detected language of the author-written side.',
    )
    translation_status = models.CharField(
        max_length=16,
        choices=TRANSLATION_STATUS_CHOICES,
        default=TRANSLATION_NONE,
        db_index=True,
    )
    translated_at = models.DateTimeField(null=True, blank=True)
    translation_fingerprint = models.CharField(
        max_length=64,
        blank=True,
        default='',
        help_text='SHA-256 of the source title+body that produced the current translation.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title


class ArticleProgress(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_progress',
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='progress_records',
    )
    progress_percent = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False, db_index=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'article_progress'
        unique_together = [('organization', 'user', 'article')]
        ordering = ['-last_viewed_at']

    def __str__(self):
        return f'{self.user_id} · {self.article_id} ({self.progress_percent}%)'


class MediaProgress(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_progress',
    )
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.CASCADE,
        related_name='progress_records',
    )
    completed = models.BooleanField(default=False, db_index=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'media_progress'
        unique_together = [('organization', 'user', 'media')]
        ordering = ['-last_viewed_at']

    def __str__(self):
        return f'{self.user_id} · {self.media_id}'
