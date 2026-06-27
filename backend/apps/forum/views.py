from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.core.permissions import IsModeratorOrAdmin
from apps.tenants.permissions import IsOrgMember

from .models import DiscussionComment, DiscussionTopic
from .serializers import (
    CommentCreateSerializer,
    DiscussionCommentSerializer,
    DiscussionTopicCreateSerializer,
    DiscussionTopicSerializer,
    ModerateSerializer,
)


class DiscussionTopicViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'

    def get_queryset(self):
        qs = DiscussionTopic.objects.select_related('author').prefetch_related('comments')
        user = self.request.user
        if user.is_authenticated and user.role.name in ('moderator', 'admin'):
            return qs
        return qs.filter(is_approved=True)

    def get_serializer_class(self):
        if self.action == 'create':
            return DiscussionTopicCreateSerializer
        return DiscussionTopicSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsOrgMember()]

    def perform_create(self, serializer):
        if self.request.user.is_suspended:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Account suspended.')
        topic = serializer.save()
        log_activity(self.request.user, 'topic_created', {'topic_id': str(topic.id)})


class TopicCommentCreateView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated, IsOrgMember]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['topic'] = self.get_topic()
        return ctx

    def get_topic(self):
        return DiscussionTopic.objects.get(id=self.kwargs['id'])

    def perform_create(self, serializer):
        if self.request.user.is_suspended:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Account suspended.')
        comment = serializer.save()
        log_activity(self.request.user, 'comment_created', {'comment_id': str(comment.id)})


class TopicModerateView(APIView):
    permission_classes = [IsModeratorOrAdmin, IsOrgMember]
    serializer_class = ModerateSerializer

    @extend_schema(request=ModerateSerializer, responses=DiscussionTopicSerializer)
    def patch(self, request, id):
        try:
            topic = DiscussionTopic.objects.get(id=id)
        except DiscussionTopic.DoesNotExist:
            return Response({'detail': 'Topic not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        topic.is_approved = serializer.validated_data['is_approved']
        topic.save(update_fields=['is_approved'])
        log_activity(request.user, 'content_moderated', {
            'type': 'topic', 'id': str(topic.id), 'approved': topic.is_approved,
        })
        return Response(DiscussionTopicSerializer(topic).data)


class CommentModerateView(APIView):
    permission_classes = [IsModeratorOrAdmin, IsOrgMember]
    serializer_class = ModerateSerializer

    @extend_schema(request=ModerateSerializer, responses=DiscussionCommentSerializer)
    def patch(self, request, id):
        try:
            comment = DiscussionComment.objects.get(id=id)
        except DiscussionComment.DoesNotExist:
            return Response({'detail': 'Comment not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment.is_approved = serializer.validated_data['is_approved']
        comment.save(update_fields=['is_approved'])
        log_activity(request.user, 'content_moderated', {
            'type': 'comment', 'id': str(comment.id), 'approved': comment.is_approved,
        })
        return Response(DiscussionCommentSerializer(comment).data)


class PendingModerationView(APIView):
    permission_classes = [IsModeratorOrAdmin, IsOrgMember]

    @extend_schema(
        responses=inline_serializer(
            name='PendingModeration',
            fields={
                'topics': DiscussionTopicSerializer(many=True),
                'comments': DiscussionCommentSerializer(many=True),
            },
        ),
    )
    def get(self, request):
        pending_topics = DiscussionTopic.objects.filter(is_approved=False).select_related('author')
        pending_comments = DiscussionComment.objects.filter(is_approved=False).select_related('author', 'topic')
        return Response({
            'topics': DiscussionTopicSerializer(pending_topics, many=True).data,
            'comments': DiscussionCommentSerializer(pending_comments, many=True).data,
        })
