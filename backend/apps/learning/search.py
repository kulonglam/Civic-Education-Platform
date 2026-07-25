"""Unified keyword search across published learning content and forum topics."""

from __future__ import annotations

from django.conf import settings
from django.db.models import Q

from apps.forum.models import DiscussionTopic
from apps.tenants.context import get_current_organization
from apps.tenants.models import Organization

from .models import Article, MediaAsset


def _resolve_search_organization() -> Organization | None:
    """Scope search to the request tenant, defaulting to the public workspace."""
    organization = get_current_organization()
    if organization is not None:
        return organization
    slug = getattr(settings, 'PUBLIC_ORGANIZATION_SLUG', 'platform-demo')
    return Organization.objects.filter(slug=slug, is_active=True).first()


def global_search(query: str, *, limit: int = 8) -> dict:
    query = (query or '').strip()
    if len(query) < 2:
        return {'query': query, 'articles': [], 'media': [], 'topics': []}

    organization = _resolve_search_organization()
    if organization is None:
        return {'query': query, 'articles': [], 'media': [], 'topics': []}

    per_type = max(1, min(limit, 20))

    articles_qs = Article.objects.filter(
        status='published',
        organization=organization,
    ).select_related('category')
    media_qs = MediaAsset.objects.filter(
        status='published',
        organization=organization,
    ).select_related('category')
    topics_qs = DiscussionTopic.objects.filter(
        is_approved=True,
        organization=organization,
    )

    article_filter = (
        Q(title__icontains=query)
        | Q(content__icontains=query)
        | Q(title_ar__icontains=query)
        | Q(content_ar__icontains=query)
    )
    media_filter = (
        Q(title__icontains=query)
        | Q(description__icontains=query)
        | Q(title_ar__icontains=query)
        | Q(description_ar__icontains=query)
    )
    topic_filter = Q(title__icontains=query) | Q(content__icontains=query)

    articles = [
        {
            'id': str(row.id),
            'title': row.title,
            'category': row.category.name if row.category_id else None,
            'published_at': row.published_at,
        }
        for row in articles_qs.filter(article_filter).order_by('-published_at')[:per_type]
    ]
    media = [
        {
            'id': str(row.id),
            'title': row.title,
            'media_type': row.media_type,
            'category': row.category.name if row.category_id else None,
            'published_at': row.published_at,
        }
        for row in media_qs.filter(media_filter).order_by('-published_at')[:per_type]
    ]
    topics = [
        {
            'id': str(row.id),
            'title': row.title,
            'created_at': row.created_at,
        }
        for row in topics_qs.filter(topic_filter).order_by('-created_at')[:per_type]
    ]

    return {
        'query': query,
        'articles': articles,
        'media': media,
        'topics': topics,
    }
