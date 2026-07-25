"""Unified keyword search across published learning content and forum topics."""

from __future__ import annotations

from django.db.models import Q

from apps.forum.models import DiscussionTopic
from apps.tenants.context import get_current_organization

from .models import Article, MediaAsset


def global_search(query: str, *, limit: int = 8) -> dict:
    query = (query or '').strip()
    if len(query) < 2:
        return {'query': query, 'articles': [], 'media': [], 'topics': []}

    per_type = max(1, min(limit, 20))
    organization = get_current_organization()

    articles_qs = Article.objects.filter(status='published').select_related('category')
    media_qs = MediaAsset.objects.filter(status='published').select_related('category')
    topics_qs = DiscussionTopic.objects.filter(is_approved=True)

    if organization is not None:
        articles_qs = articles_qs.filter(organization=organization)
        media_qs = media_qs.filter(organization=organization)
        topics_qs = topics_qs.filter(organization=organization)

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
