"""Record and query learner progress on articles and media."""

from __future__ import annotations

from django.utils import timezone

from apps.tenants.context import get_current_organization

from .models import Article, ArticleProgress, MediaAsset, MediaProgress


def _resolve_organization(resource):
    org = getattr(resource, 'organization', None) or get_current_organization()
    if org is None:
        raise ValueError('Organization context is required to record progress.')
    return org


def record_article_progress(
    user,
    article: Article,
    *,
    progress_percent: int | None = None,
    completed: bool = False,
) -> ArticleProgress:
    organization = _resolve_organization(article)
    row, created_row = ArticleProgress.objects.get_or_create(
        organization=organization,
        user=user,
        article=article,
        defaults={'progress_percent': 0},
    )
    was_completed = row.completed

    if progress_percent is not None:
        row.progress_percent = max(row.progress_percent, min(100, int(progress_percent)))

    should_complete = completed or row.progress_percent >= 90
    if should_complete:
        row.progress_percent = max(row.progress_percent, 100 if completed else row.progress_percent)
        if not row.completed:
            row.completed = True
            row.completed_at = timezone.now()

    row.last_viewed_at = timezone.now()
    row.save()

    if row.completed and not was_completed:
        from apps.gamification.services import XP_ARTICLE_COMPLETE, award_xp

        award_xp(user, XP_ARTICLE_COMPLETE, reason='article_complete')

    return row


def record_media_progress(
    user,
    media: MediaAsset,
    *,
    completed: bool = False,
) -> MediaProgress:
    organization = _resolve_organization(media)
    row, _ = MediaProgress.objects.get_or_create(
        organization=organization,
        user=user,
        media=media,
    )
    was_completed = row.completed

    row.last_viewed_at = timezone.now()
    if completed and not row.completed:
        row.completed = True
        row.completed_at = timezone.now()

    row.save()

    if row.completed and not was_completed:
        from apps.gamification.services import XP_MEDIA_COMPLETE, award_xp

        award_xp(user, XP_MEDIA_COMPLETE, reason='media_complete')

    return row
