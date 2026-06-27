from rest_framework import serializers

from .models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = [
            'id', 'code', 'name', 'price_cents', 'currency', 'interval',
            'max_members', 'max_articles', 'max_quizzes', 'features',
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'plan', 'status', 'current_period_end',
            'cancel_at_period_end', 'created_at',
        ]


class CheckoutSerializer(serializers.Serializer):
    plan_code = serializers.SlugField()
