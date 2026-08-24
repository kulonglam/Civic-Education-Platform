"""Self-service profile, avatar, data export and deactivation."""

from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.storage import upload_file

from ..serializers import ProfileUpdateSerializer, UserSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return ProfileUpdateSerializer
        return UserSerializer

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user, context={'request': request}).data)

    def update(self, request, *args, **kwargs):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user, context={'request': request}).data)


class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request=inline_serializer(
            name='AvatarUploadRequest',
            fields={'avatar': serializers.ImageField()},
        ),
        responses=inline_serializer(
            name='AvatarUploadResponse',
            fields={'avatar_url': serializers.CharField()},
        ),
    )
    def patch(self, request):
        file = request.FILES.get('avatar')
        if not file:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)
        path = f'avatars/{request.user.id}/{file.name}'
        url = upload_file(path, file.read(), file.content_type, request=request)
        if not url:
            return Response(
                {'detail': 'File upload is not available. Configure Supabase storage or local media.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        profile = request.user.profile
        profile.avatar_url = url
        profile.save(update_fields=['avatar_url'])
        return Response({'avatar_url': url})


class MyDataExportView(APIView):
    """Download the authenticated user's personal data (GDPR-style)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.learning.models import Bookmark
        from apps.quizzes.models import Certificate, QuizAttempt
        from apps.tenants.models import Membership

        user = request.user
        memberships = list(
            Membership.objects.filter(user=user)
            .select_related('organization', 'department')
            .values(
                'organization__name',
                'organization__slug',
                'role',
                'department__name',
                'created_at',
            )
        )
        attempts = list(
            QuizAttempt.objects.filter(user=user)
            .select_related('quiz')
            .order_by('-attempted_at')[:200]
            .values('quiz__title', 'score', 'passed', 'attempted_at')
        )
        certificates = list(
            Certificate.objects.filter(user=user)
            .select_related('quiz')
            .values('quiz__title', 'issued_at', 'certificate_id')
        )
        bookmarks = list(
            Bookmark.objects.filter(user=user)
            .select_related('article', 'media')
            .order_by('-created_at')[:200]
            .values(
                'id',
                'created_at',
                'article__id',
                'article__title',
                'media__id',
                'media__title',
            )
        )
        log_activity(
            user,
            'data_exported',
            {'resource': 'user_self'},
            request=request,
        )
        return Response({
            'user': UserSerializer(user).data,
            'memberships': memberships,
            'quiz_attempts': attempts,
            'certificates': certificates,
            'bookmarks': bookmarks,
            'exported_at': timezone.now().isoformat(),
        })


class DeactivateAccountView(APIView):
    """Soft-deactivate the authenticated account."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        from apps.accounts.roles import is_platform_admin

        if user.is_superuser or is_platform_admin(user):
            return Response(
                {'detail': 'Platform admin accounts cannot self-deactivate. Contact support.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.save(update_fields=['is_active'])
        from apps.accounts.session import bump_session_epoch

        bump_session_epoch(user)
        log_activity(user, 'user_deactivated', {'email': user.email}, request=request)
        return Response({'message': 'Account deactivated.'})
