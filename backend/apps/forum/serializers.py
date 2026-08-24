from rest_framework import serializers

from .constants import REPORT_REASONS
from .experts import user_is_forum_expert, user_skips_forum_queue
from .models import DiscussionComment, DiscussionTopic, ForumReport


class DiscussionCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = DiscussionComment
        fields = [
            'id', 'topic', 'author', 'author_name', 'comment',
            'is_approved', 'is_expert', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'is_expert', 'created_at']


class DiscussionTopicListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    comment_count = serializers.SerializerMethodField()
    accepted_answer_id = serializers.UUIDField(read_only=True, allow_null=True)

    class Meta:
        model = DiscussionTopic
        fields = [
            'id', 'title', 'content', 'kind', 'board', 'author', 'author_name',
            'is_approved', 'is_locked', 'accepted_answer_id', 'comment_count', 'created_at',
        ]
        read_only_fields = [
            'id', 'author', 'is_approved', 'is_locked', 'accepted_answer_id', 'created_at',
        ]

    def get_comment_count(self, obj) -> int:
        count = getattr(obj, 'comment_count', None)
        if isinstance(count, int):
            return count
        return obj.comments.filter(is_approved=True).count()


class DiscussionTopicSerializer(DiscussionTopicListSerializer):
    comments = DiscussionCommentSerializer(many=True, read_only=True)

    class Meta(DiscussionTopicListSerializer.Meta):
        fields = DiscussionTopicListSerializer.Meta.fields + ['comments']


class DiscussionTopicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionTopic
        fields = ['id', 'title', 'content', 'kind', 'board', 'is_approved']
        read_only_fields = ['id', 'is_approved']

    def create(self, validated_data):
        user = self.context['request'].user
        return DiscussionTopic.objects.create(
            author=user,
            is_approved=user_skips_forum_queue(user),
            **validated_data,
        )


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionComment
        fields = ['id', 'comment']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        topic = self.context['topic']
        return DiscussionComment.objects.create(
            topic=topic,
            author=user,
            is_approved=user_skips_forum_queue(user),
            is_expert=user_is_forum_expert(user),
            **validated_data,
        )


class ModerateSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()


class LockSerializer(serializers.Serializer):
    is_locked = serializers.BooleanField()


class AcceptAnswerSerializer(serializers.Serializer):
    comment_id = serializers.UUIDField()


class ForumReportCreateSerializer(serializers.Serializer):
    reason = serializers.ChoiceField(choices=REPORT_REASONS)
    details = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class ForumReportSerializer(serializers.ModelSerializer):
    reporter_name = serializers.CharField(source='reporter.full_name', read_only=True)
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    comment_excerpt = serializers.SerializerMethodField()

    class Meta:
        model = ForumReport
        fields = [
            'id', 'target_type', 'topic', 'topic_title', 'comment', 'comment_excerpt',
            'reason', 'details', 'reporter', 'reporter_name', 'status',
            'moderator_notes', 'created_at',
        ]
        read_only_fields = fields

    def get_comment_excerpt(self, obj) -> str:
        if obj.comment_id and obj.comment:
            return obj.comment.comment[:160]
        return ''


class ForumReportReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=[
        ForumReport.STATUS_REVIEWED,
        ForumReport.STATUS_DISMISSED,
    ])
    moderator_notes = serializers.CharField(required=False, allow_blank=True, max_length=2000)
