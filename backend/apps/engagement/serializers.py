from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.utils import get_preferred_language
from apps.tenants.context import get_current_organization

from .models import Campaign, Petition, PetitionSignature, Poll, PollOption, PollVote


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id', 'label', 'label_ar', 'sort_order', 'vote_count']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar' and data.get('label_ar'):
            data['label'] = data['label_ar']
        return data


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    user_vote_option_id = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)
    total_votes = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            'id', 'question', 'question_ar', 'description', 'description_ar',
            'status', 'closes_at', 'is_open', 'options', 'user_vote_option_id',
            'total_votes', 'created_at',
        ]

    def get_user_vote_option_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        vote = PollVote.objects.filter(poll=obj, user=request.user).first()
        return str(vote.option_id) if vote else None

    def get_total_votes(self, obj):
        return sum(opt.vote_count for opt in obj.options.all())

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('question_ar'):
                data['question'] = data['question_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class PollCreateSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)
    question_ar = serializers.CharField(max_length=500, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    description_ar = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Poll.STATUS_CHOICES, default=Poll.STATUS_OPEN)
    closes_at = serializers.DateTimeField(required=False, allow_null=True)
    options = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        max_length=8,
    )

    def validate_options(self, value):
        for item in value:
            if not (item.get('label') or '').strip():
                raise serializers.ValidationError('Each option requires a label.')
        return value

    @transaction.atomic
    def create(self, validated_data):
        organization = get_current_organization()
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(
            organization=organization,
            created_by=self.context['request'].user,
            **validated_data,
        )
        for idx, opt in enumerate(options_data):
            PollOption.objects.create(
                organization=organization,
                poll=poll,
                label=opt['label'].strip(),
                label_ar=(opt.get('label_ar') or '').strip(),
                sort_order=opt.get('sort_order', idx),
            )
        return poll


class PollVoteSerializer(serializers.Serializer):
    option_id = serializers.UUIDField()


class PetitionSerializer(serializers.ModelSerializer):
    signature_count = serializers.IntegerField(read_only=True)
    user_signed = serializers.SerializerMethodField()
    goal_reached = serializers.SerializerMethodField()

    class Meta:
        model = Petition
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'goal_signatures', 'signature_count', 'goal_reached', 'user_signed',
            'status', 'created_at',
        ]

    def get_user_signed(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return PetitionSignature.objects.filter(petition=obj, user=request.user).exists()

    def get_goal_reached(self, obj):
        return obj.signature_count >= obj.goal_signatures

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class PetitionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Petition
        fields = [
            'title', 'title_ar', 'description', 'description_ar',
            'goal_signatures', 'status',
        ]

    def create(self, validated_data):
        organization = get_current_organization()
        return Petition.objects.create(
            organization=organization,
            created_by=self.context['request'].user,
            **validated_data,
        )


class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'link_url', 'status', 'created_at',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar':
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        return data


class CampaignCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            'title', 'title_ar', 'description', 'description_ar',
            'link_url', 'status',
        ]

    def create(self, validated_data):
        organization = get_current_organization()
        return Campaign.objects.create(
            organization=organization,
            created_by=self.context['request'].user,
            **validated_data,
        )
