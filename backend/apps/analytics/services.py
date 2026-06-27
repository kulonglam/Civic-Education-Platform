import csv
import io
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Max, Q
from django.utils import timezone

from apps.learning.models import Article
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


def build_member_progress(*, date_from=None, date_to=None) -> list[dict]:
    organization = get_current_organization()
    if organization is None:
        return []

    attempts = _attempts_queryset(date_from=date_from, date_to=date_to)
    rows = []

    memberships = (
        Membership.objects.filter(organization=organization)
        .select_related('user')
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
        rows.append({
            'user_id': str(user.id),
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': membership.role,
            'quizzes_attempted': stats['attempted'] or 0,
            'quizzes_passed': stats['passed'] or 0,
            'avg_score': round(stats['avg_score'] or 0, 1),
            'certificates': cert_count,
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
        'quizzes_attempted',
        'quizzes_passed',
        'avg_score',
        'certificates',
        'last_activity',
    ])

    for row in build_member_progress(date_from=date_from, date_to=date_to):
        last_activity = row['last_activity']
        writer.writerow([
            row['email'],
            row['first_name'],
            row['last_name'],
            row['role'],
            row['quizzes_attempted'],
            row['quizzes_passed'],
            row['avg_score'],
            row['certificates'],
            last_activity.isoformat() if last_activity else '',
        ])

    return buffer.getvalue()


def parse_report_dates(request):
    return _parse_date(request.query_params.get('from')), _parse_date(request.query_params.get('to'))
