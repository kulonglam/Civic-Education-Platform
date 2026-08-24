from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from apps.core.utils import get_preferred_language
from apps.tenants.context import get_current_organization

from .calendar import google_calendar_url
from .maps import EVENT_REGION_VALUES
from .models import (
    Campaign,
    CampaignSignup,
    CivicEvent,
    CivicNews,
    EventSignup,
    Petition,
    PetitionSignature,
    Poll,
    PollOption,
    PollVote,
    SuspiciousContentReport,
)


def _skip_i18n(request) -> bool:
    return bool(request and request.query_params.get('manage') in ('1', 'true', 'yes'))


class PollOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        fields = ['id', 'label', 'label_ar', 'sort_order', 'vote_count']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and get_preferred_language(request) == 'ar' and not _skip_i18n(request) and data.get('label_ar'):
            data['label'] = data['label_ar']
        return data


class PollSerializer(serializers.ModelSerializer):
    options = PollOptionSerializer(many=True, read_only=True)
    user_vote_option_id = serializers.SerializerMethodField()
    is_open = serializers.BooleanField(read_only=True)
    total_votes = serializers.SerializerMethodField()
    results_visible = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        fields = [
            'id', 'question', 'question_ar', 'description', 'description_ar',
            'kind', 'status', 'closes_at', 'is_open', 'options',
            'user_vote_option_id', 'total_votes', 'results_visible', 'created_at',
        ]

    def get_user_vote_option_id(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        vote = PollVote.objects.filter(poll=obj, user=request.user).first()
        return str(vote.option_id) if vote else None

    def get_total_votes(self, obj) -> int:
        return sum(opt.vote_count for opt in obj.options.all())

    def get_results_visible(self, obj) -> bool:
        if not obj.is_open:
            return True
        return bool(self.get_user_vote_option_id(obj))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        manage = request and request.query_params.get('manage') in ('1', 'true', 'yes')
        if request and get_preferred_language(request) == 'ar' and not manage:
            if data.get('question_ar'):
                data['question'] = data['question_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
        if not data.get('results_visible'):
            for option in data.get('options') or []:
                option.pop('vote_count', None)
        return data


class PollCreateSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=500)
    question_ar = serializers.CharField(max_length=500, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    description_ar = serializers.CharField(required=False, allow_blank=True)
    kind = serializers.ChoiceField(choices=Poll.KIND_CHOICES, default=Poll.KIND_COMMUNITY)
    status = serializers.ChoiceField(choices=Poll.STATUS_CHOICES, default=Poll.STATUS_OPEN)
    closes_at = serializers.DateTimeField(required=False, allow_null=True)
    options = serializers.ListField(
        child=serializers.DictField(),
        min_length=2,
        max_length=8,
        required=False,
    )

    def validate_options(self, value):
        for item in value:
            if not (item.get('label') or '').strip():
                raise serializers.ValidationError('Each option requires a label.')
        return value

    def validate(self, attrs):
        if self.instance is None and not attrs.get('options'):
            raise serializers.ValidationError({'options': 'At least two options are required.'})
        return attrs

    def _sync_options(self, poll, options_data, organization):
        keep_ids = []
        for idx, opt in enumerate(options_data):
            opt_id = opt.get('id')
            option = poll.options.filter(id=opt_id).first() if opt_id else None
            if option is None:
                option = PollOption.objects.create(
                    organization=organization,
                    poll=poll,
                    label=opt['label'].strip(),
                    label_ar=(opt.get('label_ar') or '').strip(),
                    sort_order=opt.get('sort_order', idx),
                )
            else:
                option.label = opt['label'].strip()
                option.label_ar = (opt.get('label_ar') or '').strip()
                option.sort_order = opt.get('sort_order', idx)
                option.save(update_fields=['label', 'label_ar', 'sort_order'])
            keep_ids.append(option.id)
        poll.options.exclude(id__in=keep_ids).filter(vote_count=0).delete()

    @transaction.atomic
    def create(self, validated_data):
        organization = get_current_organization()
        options_data = validated_data.pop('options')
        poll = Poll.objects.create(
            organization=organization,
            created_by=self.context['request'].user,
            **validated_data,
        )
        self._sync_options(poll, options_data, organization)
        return poll

    @transaction.atomic
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if options_data is not None:
            self._sync_options(instance, options_data, instance.organization)
        return instance


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
        manage = request and request.query_params.get('manage') in ('1', 'true', 'yes')
        if request and get_preferred_language(request) == 'ar' and not manage:
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
    signup_count = serializers.SerializerMethodField()
    user_joined = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'link_url', 'status', 'created_at', 'signup_count', 'user_joined',
        ]

    def get_signup_count(self, obj) -> int:
        count = getattr(obj, 'signup_count', None)
        if count is not None:
            return count
        return obj.signups.count()

    def get_user_joined(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return CampaignSignup.objects.filter(campaign=obj, user=request.user).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        manage = request and request.query_params.get('manage') in ('1', 'true', 'yes')
        if request and get_preferred_language(request) == 'ar' and not manage:
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


class CivicNewsSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default=None)

    class Meta:
        model = CivicNews
        fields = [
            'id', 'title', 'title_ar', 'body', 'body_ar',
            'topic', 'claim_type', 'source_name', 'source_url',
            'status', 'published_at', 'created_at', 'updated_at',
            'created_by_name',
        ]
        read_only_fields = ['id', 'published_at', 'created_at', 'updated_at', 'created_by_name']

    def validate(self, attrs):
        claim = attrs.get('claim_type', getattr(self.instance, 'claim_type', None))
        source_name = attrs.get(
            'source_name',
            getattr(self.instance, 'source_name', '') if self.instance else '',
        )
        if claim == CivicNews.CLAIM_VERIFIED and not (source_name or '').strip():
            raise serializers.ValidationError({
                'source_name': 'Verified facts must name a source.',
            })
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        manage = request and request.query_params.get('manage') in ('1', 'true', 'yes')
        if request and get_preferred_language(request) == 'ar' and not manage:
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('body_ar'):
                data['body'] = data['body_ar']
        return data


class SuspiciousContentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspiciousContentReport
        fields = [
            'id', 'channel', 'description', 'source_url', 'reporter_contact',
            'status', 'moderator_notes', 'reviewed_at', 'created_at',
        ]
        read_only_fields = ['id', 'status', 'moderator_notes', 'reviewed_at', 'created_at']

    def validate_description(self, value):
        text = (value or '').strip()
        if len(text) < 40:
            raise serializers.ValidationError(
                'Describe why the content looks suspicious (at least 40 characters). '
                'Do not paste the full rumour.'
            )
        if len(text) > 2000:
            raise serializers.ValidationError('Keep the description under 2000 characters.')
        return text

    def create(self, validated_data):
        request = self.context['request']
        user = request.user if request.user.is_authenticated else None
        return SuspiciousContentReport.objects.create(
            organization=get_current_organization(),
            reporter=user,
            **validated_data,
        )


class SuspiciousContentReportReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspiciousContentReport
        fields = ['status', 'moderator_notes']

    def validate_status(self, value):
        if value not in (
            SuspiciousContentReport.STATUS_REVIEWED,
            SuspiciousContentReport.STATUS_DISMISSED,
        ):
            raise serializers.ValidationError('Status must be reviewed or dismissed.')
        return value


class CivicEventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default=None)
    registered_count = serializers.SerializerMethodField()
    spots_left = serializers.SerializerMethodField()
    user_registered = serializers.SerializerMethodField()
    user_reminder = serializers.SerializerMethodField()
    google_calendar_url = serializers.SerializerMethodField()
    is_cancelled = serializers.BooleanField(read_only=True)

    class Meta:
        model = CivicEvent
        fields = [
            'id', 'title', 'title_ar', 'description', 'description_ar',
            'location', 'location_ar', 'kind', 'starts_at', 'ends_at',
            'is_all_day', 'status', 'allows_registration', 'capacity',
            'source_name', 'source_url', 'created_at', 'updated_at',
            'created_by_name', 'registered_count', 'spots_left',
            'user_registered', 'user_reminder', 'google_calendar_url',
            'is_cancelled', 'region', 'latitude', 'longitude',
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'created_by_name',
            'registered_count', 'spots_left', 'user_registered',
            'user_reminder', 'google_calendar_url', 'is_cancelled',
        ]

    def validate_region(self, value):
        region = value or ''
        if region not in EVENT_REGION_VALUES:
            raise serializers.ValidationError(
                'Choose a mapped South Sudan state, other, or leave nationwide.',
            )
        return region

    def validate(self, attrs):
        kind = attrs.get('kind', getattr(self.instance, 'kind', None))
        if kind == CivicEvent.KIND_NATIONAL_HOLIDAY:
            attrs['allows_registration'] = False
            attrs['is_all_day'] = True
        starts_at = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        ends_at = attrs.get('ends_at', getattr(self.instance, 'ends_at', None))
        if starts_at and ends_at and ends_at < starts_at:
            raise serializers.ValidationError({'ends_at': 'End time must be after the start time.'})
        return attrs

    def _my_signup(self, obj):
        mine = getattr(obj, '_my_signups', None)
        if mine is not None:
            return mine[0] if mine else None
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated:
            return None
        return EventSignup.objects.filter(event=obj, user=request.user).first()

    def get_registered_count(self, obj):
        count = getattr(obj, 'registered_count', None)
        if count is not None:
            return count
        return obj.signups.filter(is_registered=True).count()

    def get_spots_left(self, obj):
        if not obj.capacity:
            return None
        remaining = obj.capacity - self.get_registered_count(obj)
        return max(0, remaining)

    def get_user_registered(self, obj):
        signup = self._my_signup(obj)
        return bool(signup and signup.is_registered)

    def get_user_reminder(self, obj):
        signup = self._my_signup(obj)
        return bool(signup and signup.reminder_enabled)

    def get_google_calendar_url(self, obj):
        return google_calendar_url(obj)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        manage = request and request.query_params.get('manage') in ('1', 'true', 'yes')
        if request and get_preferred_language(request) == 'ar' and not manage:
            if data.get('title_ar'):
                data['title'] = data['title_ar']
            if data.get('description_ar'):
                data['description'] = data['description_ar']
            if data.get('location_ar'):
                data['location'] = data['location_ar']
        return data


class EventRegisterSerializer(serializers.Serializer):
    registered = serializers.BooleanField()


class EventReminderSerializer(serializers.Serializer):
    reminder = serializers.BooleanField()


