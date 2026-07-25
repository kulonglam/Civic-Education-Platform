from rest_framework import serializers

from .models import Badge, UserBadge


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            'id', 'slug', 'name', 'name_ar', 'description', 'description_ar',
            'icon', 'xp_required', 'sort_order',
        ]


class EarnedBadgeSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    name_ar = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    earned_at = serializers.DateTimeField()


class GamificationSummarySerializer(serializers.Serializer):
    xp_points = serializers.IntegerField()
    level = serializers.IntegerField()
    xp_to_next_level = serializers.IntegerField()
    badges_earned = EarnedBadgeSerializer(many=True)
    badges_available = BadgeSerializer(many=True)
