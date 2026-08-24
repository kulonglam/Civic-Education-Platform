import csv
import io
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Q
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.core.branding import PLATFORM_NAME
from apps.core.i18n_report import build_translation_completeness
from apps.engagement.models import Poll
from apps.learning.models import Article, ArticleProgress, Category, MediaAsset, MediaProgress
from apps.quizzes.models import Certificate, QuizAttempt
from apps.tenants.context import get_current_organization
from apps.tenants.models import Membership

User = get_user_model()


def _parse_date(value: str | None):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def org_member_users():
    organization = get_current_organization()
    if organization is None:
        return User.objects.none()
    return User.objects.filter(
        memberships__organization=organization,
        is_active=True,
    ).distinct()


def _attempts_queryset(*, date_from=None, date_to=None):
    qs = QuizAttempt.objects.all()
    if date_from:
        qs = qs.filter(attempted_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(attempted_at__date__lte=date_to)
    return qs


def build_dashboard_summary(*, date_from=None, date_to=None) -> dict:
    thirty_days_ago = timezone.now() - timedelta(days=30)
    members = org_member_users()
    attempts = _attempts_queryset(date_from=date_from, date_to=date_to)

    total_attempts = attempts.count()
    passed_attempts = attempts.filter(passed=True).count()
    active_members = members.filter(
        activity_logs__timestamp__gte=thirty_days_ago,
    ).distinct().count()

    return {
        'total_members': members.count(),
        'active_members_30d': active_members,
        'quiz_attempts': total_attempts,
        'quiz_pass_rate': round(passed_attempts / total_attempts * 100, 1) if total_attempts else 0,
        'certificates_issued': Certificate.objects.count(),
        'published_articles': Article.objects.filter(status='published').count(),
    }


MIN_DEMOGRAPHIC_RESPONSES = 5
MIN_BUCKET_COUNT = 3


def _bucket_counts(values) -> list[dict]:
    """Aggregate labels, hiding buckets too small to publish safely."""
    counts = {}
    for raw in values:
        key = (raw or '').strip() or 'unspecified'
        counts[key] = counts.get(key, 0) + 1
    visible = []
    suppressed = 0
    for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        if count < MIN_BUCKET_COUNT:
            suppressed += count
            continue
        visible.append({'key': key, 'count': count})
    if suppressed:
        visible.append({'key': 'suppressed', 'count': suppressed})
    return visible


def build_poll_opinion_summary() -> dict:
    """Totals, option results, and coarse demographic summaries for admins."""
    polls = (
        Poll.objects.filter(status__in=[Poll.STATUS_OPEN, Poll.STATUS_CLOSED])
        .prefetch_related('options', 'votes')
        .order_by('-created_at')
    )
    payload = []
    total_responses = 0
    for poll in polls:
        options = list(poll.options.all())
        votes = list(poll.votes.all())
        total = sum(option.vote_count for option in options)
        total_responses += total
        demographics_available = total >= MIN_DEMOGRAPHIC_RESPONSES
        payload.append({
            'id': str(poll.id),
            'question': poll.question,
            'kind': poll.kind,
            'status': poll.status,
            'is_open': poll.is_open,
            'total_votes': total,
            'options': [
                {
                    'id': str(option.id),
                    'label': option.label,
                    'vote_count': option.vote_count,
                    'percent': round(option.vote_count / total * 100, 1) if total else 0,
                }
                for option in options
            ],
            'demographics_available': demographics_available,
            'regions': _bucket_counts(vote.region for vote in votes) if demographics_available else [],
            'age_bands': _bucket_counts(vote.age_band for vote in votes) if demographics_available else [],
        })
    return {
        'total_polls': len(payload),
        'total_responses': total_responses,
        'polls': payload,
    }


def build_completion_snapshot(*, platform: bool = False) -> dict:
    """Lesson and media completion rates for the current organization.

    Pass ``platform=True`` for system-wide platform-admin totals.
    """
    articles = Article.all_objects if platform else Article.objects
    media = MediaAsset.all_objects if platform else MediaAsset.objects
    lesson_progress = ArticleProgress.all_objects if platform else ArticleProgress.objects
    media_progress = MediaProgress.all_objects if platform else MediaProgress.objects

    published_lessons = articles.filter(status='published').count()
    published_media = media.filter(status='published').count()
    member_count = (
        User.objects.filter(is_active=True, memberships__isnull=False).distinct().count()
        if platform
        else org_member_users().count()
    )

    lesson_starts = lesson_progress.count()
    lesson_completions = lesson_progress.filter(completed=True).count()
    media_starts = media_progress.count()
    media_completions = media_progress.filter(completed=True).count()
    members_completed_lesson = (
        lesson_progress.filter(completed=True).values('user').distinct().count()
    )

    return {
        'published_lessons': published_lessons,
        'lesson_starts': lesson_starts,
        'lesson_completions': lesson_completions,
        'lesson_completion_rate': (
            round(lesson_completions / lesson_starts * 100, 1) if lesson_starts else 0
        ),
        'published_media': published_media,
        'media_starts': media_starts,
        'media_completions': media_completions,
        'media_completion_rate': (
            round(media_completions / media_starts * 100, 1) if media_starts else 0
        ),
        'members': member_count,
        'members_completed_lesson': members_completed_lesson,
        'member_completion_rate': (
            round(members_completed_lesson / member_count * 100, 1) if member_count else 0
        ),
    }


def build_popular_lessons(*, limit: int = 10) -> list[dict]:
    rows = (
        Article.objects.filter(status='published')
        .annotate(
            completions=Count('progress_records', filter=Q(progress_records__completed=True)),
            views=Count('progress_records'),
        )
        .order_by('-completions', '-views', 'title')[:limit]
    )
    return [
        {
            'id': str(article.id),
            'title': article.title,
            'completions': article.completions,
            'views': article.views,
        }
        for article in rows
    ]


def build_language_usage() -> list[dict]:
    member_ids = org_member_users().values_list('id', flat=True)
    values = UserProfile.objects.filter(user_id__in=member_ids).values_list(
        'preferred_language',
        flat=True,
    )
    counts: dict[str, int] = {}
    for raw in values:
        key = (raw or '').strip() or 'unspecified'
        counts[key] = counts.get(key, 0) + 1
    return [
        {'key': key, 'count': count}
        for key, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]


def build_regional_engagement() -> dict:
    """Profile regions for org members, with the same k-anonymity as poll demographics."""
    member_ids = list(org_member_users().values_list('id', flat=True))
    values = list(
        UserProfile.objects.filter(user_id__in=member_ids).values_list('region', flat=True)
    )
    stated = [value for value in values if (value or '').strip()]
    available = len(stated) >= MIN_DEMOGRAPHIC_RESPONSES
    return {
        'demographics_available': available,
        'regions': _bucket_counts(values) if available else [],
        'stated_count': len(stated),
        'member_count': len(member_ids),
    }


def build_learning_insights() -> dict:
    by_category = []
    for cat in Category.objects.annotate(article_count=Count('articles')):
        by_category.append({
            'category': cat.name,
            'slug': cat.slug,
            'article_count': cat.article_count,
        })

    tag_counts: dict[str, int] = {}
    for article in Article.objects.filter(status='published').only('tags'):
        for tag in (article.tags or []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    top_tags = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)[:10]

    return {
        'articles_by_category': by_category,
        'top_tags': [{'tag': tag, 'count': count} for tag, count in top_tags],
        'completion': build_completion_snapshot(),
        'popular_lessons': build_popular_lessons(),
        'languages': build_language_usage(),
        'regional_engagement': build_regional_engagement(),
        'translation': build_translation_completeness(),
    }


def build_member_progress(*, date_from=None, date_to=None) -> list[dict]:
    organization = get_current_organization()
    if organization is None:
        return []

    attempts = _attempts_queryset(date_from=date_from, date_to=date_to)
    rows = []

    memberships = (
        Membership.objects.filter(organization=organization)
        .select_related('user', 'department')
        .order_by('user__first_name', 'user__email')
    )

    for membership in memberships:
        user = membership.user
        user_attempts = attempts.filter(user=user)
        stats = user_attempts.aggregate(
            attempted=Count('id'),
            passed=Count('id', filter=Q(passed=True)),
            avg_score=Avg('score'),
            last_activity=Max('attempted_at'),
        )
        cert_count = Certificate.objects.filter(user=user).count()
        articles_completed = ArticleProgress.objects.filter(user=user, completed=True).count()
        media_completed = MediaProgress.objects.filter(user=user, completed=True).count()
        rows.append({
            'user_id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': membership.role,
            'department': membership.department.name if membership.department_id else None,
            'department_id': str(membership.department_id) if membership.department_id else None,
            'quizzes_attempted': stats['attempted'] or 0,
            'quizzes_passed': stats['passed'] or 0,
            'avg_score': round(stats['avg_score'] or 0, 1),
            'certificates': cert_count,
            'articles_completed': articles_completed,
            'media_completed': media_completed,
            'last_activity': stats['last_activity'],
        })

    return rows


def build_progress_csv(*, date_from=None, date_to=None) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        'email',
        'first_name',
        'last_name',
        'org_role',
        'department',
        'quizzes_attempted',
        'quizzes_passed',
        'avg_score',
        'certificates',
        'articles_completed',
        'media_completed',
        'last_activity',
    ])

    for row in build_member_progress(date_from=date_from, date_to=date_to):
        last_activity = row['last_activity']
        writer.writerow([
            row['email'],
            row['first_name'],
            row['last_name'],
            row['role'],
            row.get('department') or '',
            row['quizzes_attempted'],
            row['quizzes_passed'],
            row['avg_score'],
            row['certificates'],
            row['articles_completed'],
            row['media_completed'],
            last_activity.isoformat() if last_activity else '',
        ])

    return buffer.getvalue()


def build_institutional_report_pdf(*, date_from=None, date_to=None) -> bytes:
    """Generate a simple branded PDF summary for NGO/government reporting."""
    from io import BytesIO

    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    organization = get_current_organization()
    summary = build_dashboard_summary(date_from=date_from, date_to=date_to)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 72
    c.setFont('Helvetica-Bold', 16)
    title = organization.name if organization else PLATFORM_NAME
    c.drawString(72, y, f'{title} — Learning Report')
    y -= 28
    c.setFont('Helvetica', 11)
    period = f"{date_from or 'start'} to {date_to or 'today'}"
    c.drawString(72, y, f'Reporting period: {period}')
    y -= 24
    lines = [
        f"Total members: {summary['total_members']}",
        f"Active members (30d): {summary['active_members_30d']}",
        f"Quiz attempts: {summary['quiz_attempts']}",
        f"Pass rate: {summary['quiz_pass_rate']}%",
        f"Certificates issued: {summary['certificates_issued']}",
        f"Published articles: {summary['published_articles']}",
    ]
    for line in lines:
        c.drawString(72, y, line)
        y -= 18
    c.setFont('Helvetica-Oblique', 9)
    c.drawString(72, 48, f'Generated by {PLATFORM_NAME}')
    c.showPage()
    c.save()
    return buffer.getvalue()

def parse_report_dates(request):
    return _parse_date(request.query_params.get('from')), _parse_date(request.query_params.get('to'))


def build_my_learning_summary(user) -> dict:
    """Personal learning dashboard for the current user in the active organization."""
    organization = get_current_organization()
    if organization is None:
        return {
            'articles_completed': 0,
            'articles_in_progress': 0,
            'articles_total': 0,
            'media_completed': 0,
            'media_total': 0,
            'quizzes_attempted': 0,
            'quizzes_passed': 0,
            'avg_quiz_score': 0,
            'certificates': 0,
            'by_category': [],
            'recent_activity': [],
        }

    article_progress = ArticleProgress.objects.filter(user=user)
    media_progress = MediaProgress.objects.filter(user=user)
    attempts = QuizAttempt.objects.filter(user=user)
    passed = attempts.filter(passed=True).count()
    total_attempts = attempts.count()

    published_articles = Article.objects.filter(status='published').count()
    published_media = MediaAsset.objects.filter(status='published').count()

    by_category = []
    for cat in Category.objects.all().order_by('name'):
        by_category.append({
            'category': cat.name,
            'slug': cat.slug,
            'articles_completed': article_progress.filter(
                article__category=cat,
                completed=True,
            ).count(),
            'articles_total': Article.objects.filter(category=cat, status='published').count(),
            'media_completed': media_progress.filter(
                media__category=cat,
                completed=True,
            ).count(),
            'media_total': MediaAsset.objects.filter(category=cat, status='published').count(),
        })

    recent_activity = []
    for row in article_progress.select_related('article').order_by('-last_viewed_at')[:5]:
        recent_activity.append({
            'type': 'article',
            'id': str(row.article_id),
            'title': row.article.title,
            'completed': row.completed,
            'at': row.last_viewed_at,
        })
    for row in media_progress.select_related('media').order_by('-last_viewed_at')[:5]:
        recent_activity.append({
            'type': 'media',
            'id': str(row.media_id),
            'title': row.media.title,
            'completed': row.completed,
            'at': row.last_viewed_at,
        })
    for attempt in attempts.select_related('quiz').order_by('-attempted_at')[:5]:
        recent_activity.append({
            'type': 'quiz',
            'id': str(attempt.quiz_id),
            'title': attempt.quiz.title,
            'completed': attempt.passed,
            'at': attempt.attempted_at,
            'score': attempt.score,
        })

    recent_activity.sort(key=lambda item: item['at'] or timezone.now(), reverse=True)

    return {
        'articles_completed': article_progress.filter(completed=True).count(),
        'articles_in_progress': article_progress.filter(completed=False, progress_percent__gt=0).count(),
        'articles_total': published_articles,
        'media_completed': media_progress.filter(completed=True).count(),
        'media_total': published_media,
        'quizzes_attempted': total_attempts,
        'quizzes_passed': passed,
        'avg_quiz_score': round(attempts.aggregate(avg=Avg('score'))['avg'] or 0, 1),
        'certificates': Certificate.objects.filter(user=user).count(),
        'by_category': by_category,
        'recent_activity': recent_activity[:8],
    }
