"""Toggle and annotate saved lessons (bookmarks)."""

from __future__ import annotations

from django.db.models import BooleanField, Exists, OuterRef, QuerySet, Value

from apps.tenants.context import get_current_organization

from .models import Article, Bookmark, MediaAsset


class BookmarkError(ValueError):
    """Raised when a bookmark cannot be created or removed."""


def annotate_is_bookmarked(qs: QuerySet, user, *, target: str) -> QuerySet:
    """Annotate ``is_bookmarked`` for article (``article_id``) or media (``media_id``)."""
    if not user or not user.is_authenticated:
        return qs.annotate(is_bookmarked=Value(False, output_field=BooleanField()))
    return qs.annotate(
        is_bookmarked=Exists(
            Bookmark.objects.filter(**{target: OuterRef('pk')}, user=user),
        ),
    )


def _require_organization():
    organization = get_current_organization()
    if organization is None:
        raise BookmarkError('Organization context is required to save lessons.')
    return organization


def toggle_article_bookmark(user, article: Article) -> bool:
    """Save or unsave an article. Returns True when the article is now bookmarked."""
    if article.status != 'published':
        raise BookmarkError('Only published lessons can be saved.')
    organization = _require_organization()
    existing = Bookmark.objects.filter(user=user, article=article).first()
    if existing:
        existing.delete()
        return False
    Bookmark.objects.create(organization=organization, user=user, article=article)
    return True


def toggle_media_bookmark(user, media: MediaAsset) -> bool:
    """Save or unsave media. Returns True when the media is now bookmarked."""
    if media.status != 'published':
        raise BookmarkError('Only published lessons can be saved.')
    organization = _require_organization()
    existing = Bookmark.objects.filter(user=user, media=media).first()
    if existing:
        existing.delete()
        return False
    Bookmark.objects.create(organization=organization, user=user, media=media)
    return True
