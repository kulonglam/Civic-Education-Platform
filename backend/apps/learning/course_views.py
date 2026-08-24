from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.tenants.models import Membership
from apps.tenants.permissions import CanDeleteOrgContent, IsOrgContentEditor, get_membership

from .models import ArticleProgress, Course
from .serializers import CourseSerializer


def _can_see_unpublished_courses(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role and role.name in ('editor', 'admin', 'super_admin'):
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (
        Membership.OWNER,
        Membership.ADMIN,
        Membership.CONTENT_MANAGER,
    )


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    lookup_field = 'id'
    search_fields = ['title', 'title_ar', 'description', 'description_ar']
    ordering_fields = ['title', 'created_at']

    def get_queryset(self):
        qs = Course.objects.prefetch_related('lessons__article').all()
        if not _can_see_unpublished_courses(self.request.user):
            qs = qs.filter(status=Course.STATUS_PUBLISHED)
        return qs

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        if self.action == 'destroy':
            return [IsAuthenticated(), CanDeleteOrgContent()]
        return [IsAuthenticated(), IsOrgContentEditor()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        user = self.request.user
        if user and user.is_authenticated:
            context['completed_article_ids'] = set(
                ArticleProgress.objects.filter(user=user, completed=True)
                .values_list('article_id', flat=True)
            )
        else:
            context['completed_article_ids'] = set()
        return context

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        course = self.get_queryset().get(pk=course.pk)
        return Response(
            self.get_serializer(course).data,
            status=status.HTTP_201_CREATED,
        )
