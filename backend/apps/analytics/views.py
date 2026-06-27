from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
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
from apps.learning.models import Article, Category
from apps.quizzes.models import Quiz, QuizAttempt
from apps.tenants.context import get_current_organization

from .permissions import IsOrgAnalyticsAdmin
from .services import (
    build_dashboard_summary,
    build_member_progress,
    build_progress_csv,
    parse_report_dates,
)

User = get_user_model()


def org_users():
    """Users scoped to the current organization (all users if no tenant)."""
    organization = get_current_organization()
    qs = User.objects.all()
    if organization is not None:
        qs = qs.filter(memberships__organization=organization).distinct()
    return qs


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsOverviewView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        users = org_users()
        active_users = users.filter(
            activity_logs__timestamp__gte=thirty_days_ago
        ).distinct().count()
        return Response({
            'total_users': users.count(),
            'active_users_30d': active_users,
            'articles_published': Article.objects.filter(status='published').count(),
            'quiz_completions': QuizAttempt.objects.count(),
        })


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsQuizzesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        data = []
        for quiz in Quiz.objects.all():
            attempts = QuizAttempt.objects.filter(quiz=quiz)
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
            'total_topics': DiscussionTopic.objects.count(),
            'total_comments': DiscussionComment.objects.count(),
            'pending_topics': DiscussionTopic.objects.filter(is_approved=False).count(),
            'pending_comments': DiscussionComment.objects.filter(is_approved=False).count(),
        })


@extend_schema(responses=OpenApiTypes.OBJECT)
class AnalyticsLearningView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        by_category = []
        for cat in Category.objects.annotate(article_count=Count('articles')):
            by_category.append({
                'category': cat.name,
                'slug': cat.slug,
                'article_count': cat.article_count,
            })

        tag_counts = {}
        articles = Article.objects.filter(status='published')
        for article in articles:
            for tag in (article.tags or []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        return Response({
            'articles_by_category': by_category,
            'top_tags': [{'tag': t, 'count': c} for t, c in top_tags],
        })


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
        return Response({
            'members': build_member_progress(date_from=date_from, date_to=date_to),
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
