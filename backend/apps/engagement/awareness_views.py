from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.core.utils import get_preferred_language
from apps.learning.misinformation import (
    AWARENESS_ARTICLES,
    FACT_OR_FICTION_TITLE,
    VERIFY_LESSON_TITLE,
)
from apps.learning.models import Article
from apps.quizzes.models import Quiz
from apps.tenants.permissions import IsOrgForumModerator, IsOrgMember

from .models import SuspiciousContentReport
from .serializers import (
    SuspiciousContentReportReviewSerializer,
    SuspiciousContentReportSerializer,
)


def _localize_title(article, request):
    if request and get_preferred_language(request) == 'ar' and article.title_ar:
        return article.title_ar
    return article.title


class AwarenessOverviewView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        title_to_key = {VERIFY_LESSON_TITLE: 'verify'}
        for spec in AWARENESS_ARTICLES:
            title_to_key[spec['title']] = spec['key']

        articles = Article.objects.filter(
            title__in=title_to_key.keys(),
            status='published',
        )
        found = {article.title: article for article in articles}
        key_to_title = {'verify': VERIFY_LESSON_TITLE}
        for spec in AWARENESS_ARTICLES:
            key_to_title[spec['key']] = spec['title']
        order = ['verify'] + [spec['key'] for spec in AWARENESS_ARTICLES]
        lessons = []

        for key in order:
            title = key_to_title[key]
            article = found.get(title)
            lessons.append({
                'key': key,
                'title': _localize_title(article, request) if article else title,
                'article_id': str(article.id) if article else None,
            })

        quiz = Quiz.objects.filter(title=FACT_OR_FICTION_TITLE, is_active=True).first()
        quiz_payload = None
        if quiz is not None:
            title = quiz.title
            if request and get_preferred_language(request) == 'ar' and quiz.title_ar:
                title = quiz.title_ar
            quiz_payload = {'id': str(quiz.id), 'title': title}

        return Response({'lessons': lessons, 'quiz': quiz_payload})


class SuspiciousReportListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated(), IsOrgMember(), IsOrgForumModerator()]

    def get_throttles(self):
        if self.request.method == 'POST':
            self.throttle_scope = 'awareness_report'
            return [ScopedRateThrottle()]
        return []

    def get(self, request):
        qs = SuspiciousContentReport.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = SuspiciousContentReportSerializer(qs[:100], many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SuspiciousContentReportSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SuspiciousReportReviewView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember, IsOrgForumModerator]

    def patch(self, request, report_id):
        report = SuspiciousContentReport.objects.filter(id=report_id).first()
        if report is None:
            return Response({'detail': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = SuspiciousContentReportReviewSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        report = serializer.save(
            reviewed_by=request.user,
            reviewed_at=timezone.now(),
        )
        return Response(SuspiciousContentReportSerializer(report).data)
