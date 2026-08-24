"""Ranked learning recommendations from progress, courses, and popularity.

This is a rules-based engine (not a trained model): each candidate gets a
score and a reason code so the UI can explain why it was suggested.
"""

from __future__ import annotations

from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from apps.tenants.context import get_current_organization

from .models import Article, ArticleProgress, Bookmark, Course, MediaAsset, MediaProgress

REASON_CONTINUE_COURSE = 'continue_course'
REASON_IN_PROGRESS = 'in_progress'
REASON_BOOKMARKED = 'bookmarked'
REASON_RELATED_CATEGORY = 'related_category'
REASON_POPULAR = 'popular'
REASON_QUIZ = 'quiz'
REASON_MEDIA = 'media'
REASON_NEW = 'new_content'

MAX_ITEMS = 12


def _item(*, kind, item_id, title, title_ar, score, reason, **extra) -> dict:
    payload = {
        'kind': kind,
        'id': str(item_id),
        'title': title,
        'title_ar': title_ar or '',
        'score': score,
        'reason': reason,
        'href': _href(kind, item_id),
    }
    payload.update(extra)
    return payload


def _href(kind: str, item_id) -> str:
    if kind == 'article':
        return f'/articles/{item_id}'
    if kind == 'media':
        return f'/media/{item_id}'
    if kind == 'quiz':
        return f'/quizzes/{item_id}'
    return '/'


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in sorted(items, key=lambda row: (-row['score'], row['title'])):
        key = (item['kind'], item['id'])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
        if len(unique) >= MAX_ITEMS:
            break
    return unique


def build_recommendations(user=None) -> dict:
    organization = get_current_organization()
    if organization is None:
        return {'items': [], 'personalized': False}

    if user is None or not getattr(user, 'is_authenticated', False):
        return {'items': _anonymous_recommendations(), 'personalized': False}

    return {'items': _personalized_recommendations(user), 'personalized': True}


def _anonymous_recommendations() -> list[dict]:
    items: list[dict] = []
    popular = (
        Article.objects.filter(status='published')
        .annotate(starts=Count('progress_records'))
        .order_by('-starts', '-published_at')[:8]
    )
    for article in popular:
        items.append(_item(
            kind='article',
            item_id=article.id,
            title=article.title,
            title_ar=article.title_ar,
            score=50 + min(article.starts, 20),
            reason=REASON_POPULAR,
            category=article.category.name if article.category_id else '',
        ))
    newest = Article.objects.filter(status='published').order_by('-published_at')[:6]
    for article in newest:
        items.append(_item(
            kind='article',
            item_id=article.id,
            title=article.title,
            title_ar=article.title_ar,
            score=30,
            reason=REASON_NEW,
            category=article.category.name if article.category_id else '',
        ))
    return _dedupe(items)


def _personalized_recommendations(user) -> list[dict]:
    items: list[dict] = []
    article_progress = {
        row.article_id: row
        for row in ArticleProgress.objects.filter(user=user).select_related('article')
    }
    completed_article_ids = {
        article_id for article_id, row in article_progress.items() if row.completed
    }
    in_progress_ids = {
        article_id
        for article_id, row in article_progress.items()
        if not row.completed and row.progress_percent > 0
    }
    started_ids = set(article_progress)

    for row in article_progress.values():
        if row.article_id in in_progress_ids and row.article.status == 'published':
            items.append(_item(
                kind='article',
                item_id=row.article_id,
                title=row.article.title,
                title_ar=row.article.title_ar,
                score=90 + min(row.progress_percent, 9),
                reason=REASON_IN_PROGRESS,
                category=row.article.category.name if row.article.category_id else '',
                progress_percent=row.progress_percent,
            ))

    courses = (
        Course.objects.filter(status=Course.STATUS_PUBLISHED)
        .prefetch_related('lessons__article__category')
        .order_by('title')
    )
    for course in courses:
        for lesson in course.lessons.all():
            article = lesson.article
            if article.status != 'published':
                continue
            if article.id in completed_article_ids:
                continue
            extra_score = 8 if article.id in in_progress_ids else 0
            items.append(_item(
                kind='article',
                item_id=article.id,
                title=article.title,
                title_ar=article.title_ar,
                score=100 + extra_score,
                reason=REASON_CONTINUE_COURSE,
                category=article.category.name if article.category_id else '',
                course_id=str(course.id),
                course_title=course.title,
            ))
            break

    bookmarks = Bookmark.objects.filter(user=user).select_related('article', 'media')[:12]
    for bookmark in bookmarks:
        if bookmark.article_id and bookmark.article.status == 'published':
            if bookmark.article_id in completed_article_ids:
                continue
            items.append(_item(
                kind='article',
                item_id=bookmark.article_id,
                title=bookmark.article.title,
                title_ar=bookmark.article.title_ar,
                score=80,
                reason=REASON_BOOKMARKED,
                category=bookmark.article.category.name if bookmark.article.category_id else '',
            ))
        elif bookmark.media_id and bookmark.media.status == 'published':
            items.append(_item(
                kind='media',
                item_id=bookmark.media_id,
                title=bookmark.media.title,
                title_ar=bookmark.media.title_ar,
                score=78,
                reason=REASON_BOOKMARKED,
            ))

    category_ids = {
        row.article.category_id
        for row in article_progress.values()
        if row.completed and row.article.category_id
    }
    if category_ids:
        related = (
            Article.objects.filter(status='published', category_id__in=category_ids)
            .exclude(id__in=started_ids)
            .order_by('-published_at')[:8]
        )
        for article in related:
            items.append(_item(
                kind='article',
                item_id=article.id,
                title=article.title,
                title_ar=article.title_ar,
                score=62,
                reason=REASON_RELATED_CATEGORY,
                category=article.category.name if article.category_id else '',
            ))

    popular = (
        Article.objects.filter(status='published')
        .exclude(id__in=started_ids)
        .annotate(starts=Count('progress_records'))
        .order_by('-starts', '-published_at')[:8]
    )
    for article in popular:
        items.append(_item(
            kind='article',
            item_id=article.id,
            title=article.title,
            title_ar=article.title_ar,
            score=50 + min(article.starts, 15),
            reason=REASON_POPULAR,
            category=article.category.name if article.category_id else '',
        ))

    from apps.quizzes.models import Quiz, QuizAttempt

    attempted_quiz_ids = set(
        QuizAttempt.objects.filter(user=user).values_list('quiz_id', flat=True)
    )
    quizzes = Quiz.objects.filter(is_active=True).exclude(id__in=attempted_quiz_ids).order_by('-created_at')[:6]
    for quiz in quizzes:
        items.append(_item(
            kind='quiz',
            item_id=quiz.id,
            title=quiz.title,
            title_ar=quiz.title_ar,
            score=46,
            reason=REASON_QUIZ,
        ))

    completed_media_ids = set(
        MediaProgress.objects.filter(user=user, completed=True).values_list('media_id', flat=True)
    )
    media_qs = MediaAsset.objects.filter(status='published').exclude(id__in=completed_media_ids).order_by('-published_at')[:6]
    for media in media_qs:
        items.append(_item(
            kind='media',
            item_id=media.id,
            title=media.title,
            title_ar=media.title_ar,
            score=40,
            reason=REASON_MEDIA,
        ))

    week_ago = timezone.now() - timedelta(days=21)
    newest = (
        Article.objects.filter(status='published', published_at__gte=week_ago)
        .exclude(id__in=started_ids)
        .order_by('-published_at')[:4]
    )
    for article in newest:
        items.append(_item(
            kind='article',
            item_id=article.id,
            title=article.title,
            title_ar=article.title_ar,
            score=32,
            reason=REASON_NEW,
            category=article.category.name if article.category_id else '',
        ))

    return _dedupe(items)
