from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.billing.services import check_quota
from apps.core.storage import get_signed_url
from apps.notifications.services import notify_user
from apps.tenants.context import get_current_organization
from apps.tenants.models import Membership
from apps.tenants.permissions import IsOrgContentEditor, IsOrgMember, get_membership

from .models import Certificate, Quiz, QuizAttempt
from .serializers import (
    CertificateSerializer,
    QuizAttemptSerializer,
    QuizAttemptSubmitSerializer,
    QuizSerializer,
    QuizWriteSerializer,
)
from .services import generate_certificate_number
from .tasks import generate_certificate_pdf_task


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        qs = Quiz.objects.prefetch_related('questions')
        user = self.request.user
        if user.is_authenticated:
            role = getattr(user.role, 'name', None)
            if role in ('editor', 'admin'):
                return qs
            membership = get_membership(user)
            if membership and membership.role in (
                Membership.OWNER,
                Membership.ADMIN,
                Membership.CONTENT_MANAGER,
            ):
                return qs
        return qs.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return QuizWriteSerializer
        return QuizSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsOrgMember(), IsOrgContentEditor()]
        return [IsAuthenticated(), IsOrgMember()]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        user = self.request.user
        is_editor = False
        if user.is_authenticated:
            role = getattr(user.role, 'name', None)
            if role in ('editor', 'admin'):
                is_editor = True
            else:
                membership = get_membership(user)
                is_editor = bool(
                    membership
                    and membership.role
                    in (Membership.OWNER, Membership.ADMIN, Membership.CONTENT_MANAGER)
                )
        ctx['hide_answers'] = self.action in ('list', 'retrieve') and not is_editor
        return ctx

    def perform_create(self, serializer):
        organization = get_current_organization()
        if organization is not None:
            check_quota(organization, 'quizzes')
        quiz = serializer.save()
        log_activity(self.request.user, 'quiz_created', {'quiz_id': str(quiz.id)})


class QuizAttemptView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = QuizAttemptSubmitSerializer

    @extend_schema(
        request=QuizAttemptSubmitSerializer,
        responses=inline_serializer(
            name='QuizAttemptResult',
            fields={
                'attempt': QuizAttemptSerializer(),
                'certificate': CertificateSerializer(allow_null=True),
            },
        ),
    )
    def post(self, request, id):
        try:
            quiz = Quiz.objects.prefetch_related('questions').get(id=id, is_active=True)
        except Quiz.DoesNotExist:
            return Response({'detail': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuizAttemptSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        answers = serializer.validated_data['answers']

        score = 0
        max_score = 0
        for question in quiz.questions.all():
            max_score += question.points
            user_answer = answers.get(str(question.id), '')
            if user_answer == question.correct_answer:
                score += question.points

        percentage = int((score / max_score * 100)) if max_score > 0 else 0
        passed = percentage >= quiz.passing_score

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=request.user,
            answers=answers,
            score=percentage,
            max_score=100,
            passed=passed,
        )
        log_activity(request.user, 'quiz_attempt', {
            'quiz_id': str(quiz.id),
            'score': percentage,
            'passed': passed,
        })

        notify_user(
            request.user,
            'quiz_result',
            'Quiz result',
            f'You scored {percentage}% on "{quiz.title}". {"Passed!" if passed else "Try again."}',
        )

        certificate_data = None
        if passed:
            cert_number = generate_certificate_number()
            certificate = Certificate.objects.create(
                certificate_number=cert_number,
                quiz=quiz,
                user=request.user,
                attempt=attempt,
            )
            # PDF render + upload runs off the request path; the download
            # endpoint already handles a not-yet-ready pdf_url.
            generate_certificate_pdf_task.delay(str(certificate.id))
            log_activity(request.user, 'certificate_issued', {
                'certificate_id': str(certificate.id),
            })
            notify_user(
                request.user,
                'certificate',
                'Certificate issued',
                f'Congratulations! Your certificate {cert_number} has been issued.',
            )
            certificate_data = CertificateSerializer(certificate).data

        return Response({
            'attempt': QuizAttemptSerializer(attempt).data,
            'certificate': certificate_data,
        })


class QuizResultsView(generics.ListAPIView):
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return QuizAttempt.objects.none()
        return QuizAttempt.objects.filter(user=self.request.user).select_related('quiz')


class CertificateListView(generics.ListAPIView):
    serializer_class = CertificateSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Certificate.objects.none()
        return Certificate.objects.filter(user=self.request.user).select_related('quiz')


class CertificateDownloadView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = CertificateSerializer

    @extend_schema(
        responses=inline_serializer(
            name='CertificateDownload',
            fields={'download_url': serializers.CharField()},
        ),
    )
    def get(self, request, id):
        try:
            certificate = Certificate.objects.get(id=id, user=request.user)
        except Certificate.DoesNotExist:
            return Response({'detail': 'Certificate not found.'}, status=status.HTTP_404_NOT_FOUND)

        if certificate.pdf_url:
            signed = get_signed_url(f'certificates/{certificate.id}.pdf')
            return Response({'download_url': signed or certificate.pdf_url})
        return Response({'detail': 'PDF not available.'}, status=status.HTTP_404_NOT_FOUND)
