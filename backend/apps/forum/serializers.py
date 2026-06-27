from rest_framework import serializers

from .models import DiscussionComment, DiscussionTopic


class DiscussionCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    class Meta:
        model = DiscussionComment
        fields = ['id', 'topic', 'author', 'author_name', 'comment', 'is_approved', 'created_at']
        read_only_fields = ['id', 'author', 'is_approved', 'created_at']


class DiscussionTopicSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)
    comments = DiscussionCommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = DiscussionTopic
        fields = [
            'id', 'title', 'content', 'author', 'author_name',
            'is_approved', 'comments', 'comment_count', 'created_at',
        ]
        read_only_fields = ['id', 'author', 'is_approved', 'created_at']

    def get_comment_count(self, obj) -> int:
        return obj.comments.filter(is_approved=True).count()


class DiscussionTopicCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionTopic
        fields = ['id', 'title', 'content', 'is_approved']
        read_only_fields = ['id', 'is_approved']

    def create(self, validated_data):
        user = self.context['request'].user
        is_moderator = user.role.name in ('moderator', 'admin')
        return DiscussionTopic.objects.create(
            author=user,
            is_approved=is_moderator,
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
        is_moderator = user.role.name in ('moderator', 'admin')
        return DiscussionComment.objects.create(
            topic=topic,
            author=user,
            is_approved=is_moderator,
            **validated_data,
        )


class ModerateSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
