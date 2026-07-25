from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=4000, trim_whitespace=True)
    article_id = serializers.UUIDField(required=False, allow_null=True)


class TutorSourceSerializer(serializers.Serializer):
    article_id = serializers.UUIDField(required=False, allow_null=True)
    title = serializers.CharField()
    source = serializers.CharField()
    category = serializers.CharField()
    category_slug = serializers.CharField()
    source_kind = serializers.CharField()
    excerpt = serializers.CharField()


class ChatResponseSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    reply = serializers.CharField()
    sources = TutorSourceSerializer(many=True, required=False)
    tokens_used = serializers.IntegerField()
    messages_used_today = serializers.IntegerField()
    daily_limit = serializers.IntegerField(allow_null=True)
    messages_remaining = serializers.IntegerField(allow_null=True, required=False)


class TutorUsageSerializer(serializers.Serializer):
    daily_limit = serializers.IntegerField(allow_null=True)
    messages_used_today = serializers.IntegerField()
    messages_remaining = serializers.IntegerField(allow_null=True)
    session_message_count = serializers.IntegerField()


class TutorMessageSerializer(serializers.Serializer):
    role = serializers.CharField()
    content = serializers.CharField()


class TutorSessionSerializer(serializers.Serializer):
    session_id = serializers.CharField()
    article_id = serializers.UUIDField(required=False, allow_null=True)
    messages = TutorMessageSerializer(many=True)


class TutorSessionSummarySerializer(serializers.Serializer):
    session_id = serializers.CharField()
    preview = serializers.CharField()
    turns = serializers.IntegerField()
    started_at = serializers.DateTimeField()
    last_at = serializers.DateTimeField()
    article_id = serializers.UUIDField(required=False, allow_null=True)
