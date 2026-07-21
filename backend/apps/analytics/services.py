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
    title = organization.name if organization else 'Civic Education Platform'
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
    c.drawString(72, 48, 'Generated by Civic Education Platform')
    c.showPage()
    c.save()
    return buffer.getvalue()

def parse_report_dates(request):
    return _parse_date(request.query_params.get('from')), _parse_date(request.query_params.get('to'))
