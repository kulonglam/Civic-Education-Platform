from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg
from django.http import HttpResponse
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.billing.services import require_analytics
from apps.core.permissions import IsAdmin
from apps.forum.models import DiscussionComment, DiscussionTopic
from apps.learning.models import Article
from apps.quizzes.models import Quiz, QuizAttempt
from apps.tenants.context import get_current_organization
from apps.tenants.permissions import IsOrgMember

from .permissions import IsOrgAnalyticsAdmin
from .services import (
    build_completion_snapshot,
    build_dashboard_summary,
    build_institutional_report_pdf,
    build_learning_insights,
    build_member_progress,
    build_my_learning_summary,
    build_poll_opinion_summary,
    build_progress_csv,
    parse_report_dates,
)

User = get_user_model()


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsOverviewView(APIView):
    """System-wide KPIs for platform administrators (not tenant-scoped)."""

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        users = User.objects.filter(is_active=True)
        active_users = users.filter(
            activity_logs__timestamp__gte=thirty_days_ago
        ).distinct().count()
        completion = build_completion_snapshot(platform=True)
        return Response({
            'total_users': users.count(),
            'active_users_30d': active_users,
            'articles_published': Article.all_objects.filter(status='published').count(),
            'quiz_completions': QuizAttempt.all_objects.count(),
            'lesson_completion_rate': completion['lesson_completion_rate'],
            'media_completion_rate': completion['media_completion_rate'],
            'member_completion_rate': completion['member_completion_rate'],
        })


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsQuizzesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        data = []
        for quiz in Quiz.all_objects.all():
            attempts = QuizAttempt.all_objects.filter(quiz=quiz)
            total = attempts.count()
            passed = attempts.filter(passed=True).count()
            data.append({
                'quiz_id': str(quiz.id),
                'title': quiz.title,
                'attempt_count': total,
                'pass_rate': round(passed / total * 100, 1) if total else 0,
                'avg_score': round(attempts.aggregate(avg=Avg('score'))['avg'] or 0, 1),
            })
        return Response(data)


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsForumView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({
            'total_topics': DiscussionTopic.all_objects.count(),
            'total_comments': DiscussionComment.all_objects.count(),
            'pending_topics': DiscussionTopic.all_objects.filter(is_approved=False).count(),
            'pending_comments': DiscussionComment.all_objects.filter(is_approved=False).count(),
        })


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsPollsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response(build_poll_opinion_summary())


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsLearningView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response(build_learning_insights())


@extend_schema(responses=OpenApiTypes.OBJECT)
class MyLearningView(APIView):
    """Personal learning progress for the authenticated member."""

    permission_classes = [IsAuthenticated, IsOrgMember]

    def get(self, request):
        return Response(build_my_learning_summary(request.user))


@extend_schema(responses=OpenApiTypes.OBJECT)
class OrgDashboardView(APIView):
    """Organization KPIs for school/NGO admins on paid plans."""

    permission_classes = [IsAuthenticated, IsOrgAnalyticsAdmin]

    def get(self, request):
        require_analytics(get_current_organization())
        date_from, date_to = parse_report_dates(request)
        return Response(build_dashboard_summary(date_from=date_from, date_to=date_to))


@extend_schema(
    responses=OpenApiTypes.OBJECT,
    parameters=[
        OpenApiParameter(name='from', type=str, description='Start date (YYYY-MM-DD)'),
        OpenApiParameter(name='to', type=str, description='End date (YYYY-MM-DD)'),
    ],
)
class MemberProgressView(APIView):
    """Per-member quiz progress for the current organization."""

    permission_classes = [IsAuthenticated, IsOrgAnalyticsAdmin]

    def get(self, request):
        require_analytics(get_current_organization())
        date_from, date_to = parse_report_dates(request)
        members = build_member_progress(date_from=date_from, date_to=date_to)
        department = request.query_params.get('department')
        if department:
            members = [m for m in members if m.get('department_id') == department]
        return Response({
            'members': members,
        })


@extend_schema(
    responses={(200, 'text/csv'): OpenApiTypes.BINARY},
    parameters=[
        OpenApiParameter(name='from', type=str, description='Start date (YYYY-MM-DD)'),
        OpenApiParameter(name='to', type=str, description='End date (YYYY-MM-DD)'),
    ],
)
class ExportProgressCSVView(APIView):
    """Download learner progress as CSV (Pro/Enterprise plans)."""

    permission_classes = [IsAuthenticated, IsOrgAnalyticsAdmin]

    def get(self, request):
        organization = get_current_organization()
        require_analytics(organization)
        date_from, date_to = parse_report_dates(request)
        csv_content = build_progress_csv(date_from=date_from, date_to=date_to)
        filename = f'{organization.slug}-progress.csv'
        response = HttpResponse(csv_content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


@extend_schema(
    responses={(200, 'application/pdf'): OpenApiTypes.BINARY},
    parameters=[
        OpenApiParameter(name='from', type=str, description='Start date (YYYY-MM-DD)'),
        OpenApiParameter(name='to', type=str, description='End date (YYYY-MM-DD)'),
    ],
)
class InstitutionalReportPDFView(APIView):
    """Branded PDF summary for institutional / funder reporting."""

    permission_classes = [IsAuthenticated, IsOrgAnalyticsAdmin]

    def get(self, request):
        from apps.audit.services import log_activity

        organization = get_current_organization()
        require_analytics(organization)
        date_from, date_to = parse_report_dates(request)
        pdf_bytes = build_institutional_report_pdf(date_from=date_from, date_to=date_to)
        log_activity(
            request.user,
            'data_exported',
            {'resource': 'institutional_report_pdf'},
            organization=organization,
            request=request,
        )
        filename = f'{organization.slug}-learning-report.pdf'
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
