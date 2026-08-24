from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.audit.services import log_activity
from apps.tenants.models import Membership
from apps.tenants.permissions import IsOrgForumModerator, IsOrgMember, get_membership

from .models import DiscussionComment, DiscussionTopic, ForumReport
from .serializers import (
    AcceptAnswerSerializer,
    CommentCreateSerializer,
    DiscussionCommentSerializer,
    DiscussionTopicCreateSerializer,
    DiscussionTopicListSerializer,
    DiscussionTopicSerializer,
    ForumReportCreateSerializer,
    ForumReportReviewSerializer,
    ForumReportSerializer,
    LockSerializer,
    ModerateSerializer,
)


def _can_moderate_forum(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, 'role', None)
    if role and role.name in ('moderator', 'admin'):
        return True
    membership = get_membership(user)
    return membership is not None and membership.role in (
        Membership.OWNER,
        Membership.ADMIN,
        Membership.MODERATOR,
    )


def _topic_queryset(user):
    qs = DiscussionTopic.objects.select_related('author', 'accepted_answer').annotate(
        comment_count=Count('comments', filter=Q(comments__is_approved=True), distinct=True),
    )
    if _can_moderate_forum(user):
        return qs.prefetch_related('comments__author')
    approved_comments = DiscussionComment.objects.filter(is_approved=True).select_related('author')
    return qs.filter(is_approved=True).prefetch_related(
        Prefetch('comments', queryset=approved_comments),
    )


def _create_forum_report(*, user, topic, reason, details, comment=None):
    pending = ForumReport.objects.filter(
        reporter=user,
        topic=topic,
        comment=comment,
        status=ForumReport.STATUS_PENDING,
    )
    if pending.exists():
        raise ValidationError({'detail': 'You already have a pending report for this post.'})
    return ForumReport.objects.create(
        reporter=user,
        topic=topic,
        comment=comment,
        target_type=ForumReport.TARGET_COMMENT if comment is not None else ForumReport.TARGET_TOPIC,
        reason=reason,
        details=details,
    )


class DiscussionTopicViewSet(viewsets.ModelViewSet):
    lookup_field = 'id'
    filterset_fields = ['kind', 'board']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'comment_count']
    ordering = ['-created_at']

    def get_queryset(self):
        return _topic_queryset(self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return DiscussionTopicCreateSerializer
        if self.action == 'list':
            return DiscussionTopicListSerializer
        return DiscussionTopicSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsOrgMember()]

    def perform_create(self, serializer):
        if self.request.user.is_suspended:
            raise PermissionDenied('Account suspended.')
        topic = serializer.save()
        log_activity(self.request.user, 'topic_created', {'topic_id': str(topic.id)})


class TopicCommentCreateView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = CommentCreateSerializer

    def get_topic(self):
        return get_object_or_404(DiscussionTopic, id=self.kwargs['id'])

    def post(self, request, id):
        if request.user.is_suspended:
            raise PermissionDenied('Account suspended.')
        topic = self.get_topic()
        if topic.is_locked and not _can_moderate_forum(request.user):
            raise PermissionDenied('This discussion is locked.')
        if (
            not topic.is_approved
            and topic.author_id != request.user.id
            and not _can_moderate_forum(request.user)
        ):
            raise PermissionDenied('This topic is not open for comments yet.')
        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request, 'topic': topic},
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        log_activity(request.user, 'comment_created', {'comment_id': str(comment.id)})
        return Response(CommentCreateSerializer(comment).data, status=status.HTTP_201_CREATED)


class TopicModerateView(APIView):
    permission_classes = [IsOrgForumModerator, IsOrgMember]
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


class TopicLockView(APIView):
    permission_classes = [IsOrgForumModerator, IsOrgMember]
    serializer_class = LockSerializer

    @extend_schema(request=LockSerializer, responses=DiscussionTopicListSerializer)
    def patch(self, request, id):
        try:
            topic = DiscussionTopic.objects.get(id=id)
        except DiscussionTopic.DoesNotExist:
            return Response({'detail': 'Topic not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = LockSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        topic.is_locked = serializer.validated_data['is_locked']
        topic.save(update_fields=['is_locked'])
        log_activity(request.user, 'topic_locked', {
            'id': str(topic.id), 'is_locked': topic.is_locked,
        })
        return Response(DiscussionTopicListSerializer(topic).data)


class TopicAcceptAnswerView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = AcceptAnswerSerializer

    @extend_schema(request=AcceptAnswerSerializer, responses=DiscussionTopicSerializer)
    def post(self, request, id):
        try:
            topic = DiscussionTopic.objects.get(id=id)
        except DiscussionTopic.DoesNotExist:
            return Response({'detail': 'Topic not found.'}, status=status.HTTP_404_NOT_FOUND)
        if topic.kind != DiscussionTopic.KIND_QUESTION:
            raise ValidationError({'detail': 'Only questions can have an accepted answer.'})
        if topic.author_id != request.user.id and not _can_moderate_forum(request.user):
            raise PermissionDenied('Only the question author or a moderator can accept an answer.')
        serializer = AcceptAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment = DiscussionComment.objects.filter(
            id=serializer.validated_data['comment_id'],
            topic=topic,
            is_approved=True,
        ).first()
        if comment is None:
            raise ValidationError({'detail': 'Choose an approved reply on this question.'})
        topic.accepted_answer = comment
        topic.save(update_fields=['accepted_answer'])
        return Response(DiscussionTopicSerializer(topic).data)


class TopicReportView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = ForumReportCreateSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'forum_report'

    @extend_schema(request=ForumReportCreateSerializer, responses=ForumReportSerializer)
    def post(self, request, id):
        topic = get_object_or_404(DiscussionTopic, id=id)
        serializer = ForumReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = _create_forum_report(
            user=request.user,
            topic=topic,
            reason=serializer.validated_data['reason'],
            details=serializer.validated_data.get('details', ''),
        )
        log_activity(request.user, 'forum_report_created', {
            'report_id': str(report.id), 'target_type': report.target_type,
        })
        return Response(ForumReportSerializer(report).data, status=status.HTTP_201_CREATED)


class CommentReportView(APIView):
    permission_classes = [IsAuthenticated, IsOrgMember]
    serializer_class = ForumReportCreateSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'forum_report'

    @extend_schema(request=ForumReportCreateSerializer, responses=ForumReportSerializer)
    def post(self, request, id):
        comment = get_object_or_404(DiscussionComment, id=id)
        serializer = ForumReportCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = _create_forum_report(
            user=request.user,
            topic=comment.topic,
            comment=comment,
            reason=serializer.validated_data['reason'],
            details=serializer.validated_data.get('details', ''),
        )
        log_activity(request.user, 'forum_report_created', {
            'report_id': str(report.id), 'target_type': report.target_type,
        })
        return Response(ForumReportSerializer(report).data, status=status.HTTP_201_CREATED)


class ForumReportReviewView(APIView):
    permission_classes = [IsOrgForumModerator, IsOrgMember]
    serializer_class = ForumReportReviewSerializer

    @extend_schema(request=ForumReportReviewSerializer, responses=ForumReportSerializer)
    def patch(self, request, id):
        report = ForumReport.objects.filter(id=id).select_related('topic', 'comment').first()
        if report is None:
            return Response({'detail': 'Report not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ForumReportReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report.status = serializer.validated_data['status']
        report.moderator_notes = serializer.validated_data.get('moderator_notes', '')
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save(update_fields=['status', 'moderator_notes', 'reviewed_by', 'reviewed_at', 'updated_at'])
        if report.status == ForumReport.STATUS_REVIEWED:
            if report.target_type == ForumReport.TARGET_COMMENT and report.comment_id:
                comment = report.comment
                comment.is_approved = False
                comment.save(update_fields=['is_approved'])
                topic = comment.topic
                if topic.accepted_answer_id == comment.id:
                    topic.accepted_answer = None
                    topic.save(update_fields=['accepted_answer'])
            else:
                topic = report.topic
                topic.is_approved = False
                topic.save(update_fields=['is_approved'])
        log_activity(request.user, 'forum_report_reviewed', {
            'report_id': str(report.id), 'status': report.status,
        })
        return Response(ForumReportSerializer(report).data)


class CommentModerateView(APIView):
    permission_classes = [IsOrgForumModerator, IsOrgMember]
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
    permission_classes = [IsOrgForumModerator, IsOrgMember]

    @extend_schema(
        responses=inline_serializer(
            name='PendingModeration',
            fields={
                'topics': DiscussionTopicListSerializer(many=True),
                'comments': DiscussionCommentSerializer(many=True),
                'reports': ForumReportSerializer(many=True),
            },
        ),
    )
    def get(self, request):
        pending_topics = DiscussionTopic.objects.filter(is_approved=False).select_related('author')
        pending_comments = DiscussionComment.objects.filter(is_approved=False).select_related('author', 'topic')
        pending_reports = ForumReport.objects.filter(
            status=ForumReport.STATUS_PENDING,
        ).select_related('reporter', 'topic', 'comment')
        return Response({
            'topics': DiscussionTopicListSerializer(pending_topics, many=True).data,
            'comments': DiscussionCommentSerializer(pending_comments, many=True).data,
            'reports': ForumReportSerializer(pending_reports, many=True).data,
        })
