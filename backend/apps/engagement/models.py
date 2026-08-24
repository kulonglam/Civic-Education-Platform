import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.tenants.models import TenantModel


class Poll(TenantModel):
    STATUS_DRAFT = 'draft'
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]
    KIND_EDUCATIONAL = 'educational'
    KIND_COMMUNITY = 'community'
    KIND_CHOICES = [
        (KIND_EDUCATIONAL, 'Educational'),
        (KIND_COMMUNITY, 'Community'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    question_ar = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        default=KIND_COMMUNITY,
        db_index=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    closes_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='polls_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'polls'
        ordering = ['-created_at']

    def __str__(self):
        return self.question

    @property
    def is_open(self) -> bool:
        if self.status != self.STATUS_OPEN:
            return False
        if self.closes_at and self.closes_at <= timezone.now():
            return False
        return True


class PollOption(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    label_ar = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    vote_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'poll_options'
        ordering = ['sort_order', 'label']

    def __str__(self):
        return self.label


class PollVote(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='votes')
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='poll_votes',
    )
    region = models.CharField(max_length=40, blank=True, default='')
    age_band = models.CharField(max_length=20, blank=True, default='')
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'poll_votes'
        unique_together = [('organization', 'poll', 'user')]

    def __str__(self):
        return f'{self.user_id} · {self.poll_id}'


class Petition(TenantModel):
    STATUS_DRAFT = 'draft'
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    goal_signatures = models.PositiveIntegerField(default=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='petitions_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'petitions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def signature_count(self) -> int:
        return self.signatures.count()


class PetitionSignature(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    petition = models.ForeignKey(Petition, on_delete=models.CASCADE, related_name='signatures')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='petition_signatures',
    )
    signed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'petition_signatures'
        unique_together = [('organization', 'petition', 'user')]

    def __str__(self):
        return f'{self.user_id} · {self.petition_id}'


class Campaign(TenantModel):
    STATUS_DRAFT = 'draft'
    STATUS_ACTIVE = 'active'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    link_url = models.URLField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='campaigns_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class CampaignSignup(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='signups')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='campaign_signups',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaign_signups'
        unique_together = [('organization', 'campaign', 'user')]

    def __str__(self):
        return f'{self.user_id} · {self.campaign_id}'


class CivicNews(TenantModel):
    """Public civic information with an explicit claim-type label.

    Claim types are required so readers can tell verified facts from
    educational explainers, opinions, and unverified reports.
    """

    TOPIC_ANNOUNCEMENT = 'announcement'
    TOPIC_EDUCATION_UPDATE = 'education_update'
    TOPIC_ELECTION = 'election'
    TOPIC_LAW_POLICY = 'law_policy'
    TOPIC_AWARENESS = 'awareness'
    TOPIC_CHOICES = [
        (TOPIC_ANNOUNCEMENT, 'Government announcement'),
        (TOPIC_EDUCATION_UPDATE, 'Civic education update'),
        (TOPIC_ELECTION, 'Election information'),
        (TOPIC_LAW_POLICY, 'New laws and policies'),
        (TOPIC_AWARENESS, 'Public awareness campaign'),
    ]

    CLAIM_VERIFIED = 'verified_fact'
    CLAIM_EDUCATIONAL = 'educational'
    CLAIM_OPINION = 'opinion'
    CLAIM_UNVERIFIED = 'unverified'
    CLAIM_CHOICES = [
        (CLAIM_VERIFIED, 'Verified fact'),
        (CLAIM_EDUCATIONAL, 'Educational explanation'),
        (CLAIM_OPINION, 'Opinion'),
        (CLAIM_UNVERIFIED, 'Unverified information'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_ARCHIVED, 'Archived'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    body_ar = models.TextField(blank=True)
    topic = models.CharField(max_length=32, choices=TOPIC_CHOICES, db_index=True)
    claim_type = models.CharField(
        max_length=32,
        choices=CLAIM_CHOICES,
        default=CLAIM_EDUCATIONAL,
        db_index=True,
        help_text='Never treat a missing label as a verified fact.',
    )
    source_name = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='civic_news_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'civic_news'
        ordering = ['-published_at', '-created_at']
        verbose_name = 'civic news item'
        verbose_name_plural = 'civic news'

    def __str__(self):
        return self.title


class SuspiciousContentReport(TenantModel):
    """Citizen report of suspected misinformation. Not a republication of the rumour."""

    CHANNEL_WHATSAPP = 'whatsapp'
    CHANNEL_FACEBOOK = 'facebook'
    CHANNEL_WEBSITE = 'website'
    CHANNEL_RADIO = 'radio'
    CHANNEL_OTHER = 'other'
    CHANNEL_CHOICES = [
        (CHANNEL_WHATSAPP, 'WhatsApp or messaging app'),
        (CHANNEL_FACEBOOK, 'Facebook or other social page'),
        (CHANNEL_WEBSITE, 'Website'),
        (CHANNEL_RADIO, 'Radio or TV'),
        (CHANNEL_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_REVIEWED = 'reviewed'
    STATUS_DISMISSED = 'dismissed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.CharField(max_length=32, choices=CHANNEL_CHOICES, db_index=True)
    description = models.TextField(
        help_text='Why the content looks suspicious. Do not paste the full rumour to spread it.',
    )
    source_url = models.CharField(max_length=500, blank=True, default='')
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspicious_content_reports',
    )
    reporter_contact = models.EmailField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    moderator_notes = models.TextField(blank=True, default='')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suspicious_reports_reviewed',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'suspicious_content_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.channel} · {self.status}'


class CivicEvent(TenantModel):
    """Public civic calendar item: elections, hearings, workshops, holidays."""

    KIND_ELECTION = 'election'
    KIND_PUBLIC_CONSULTATION = 'public_consultation'
    KIND_COMMUNITY_MEETING = 'community_meeting'
    KIND_WORKSHOP = 'workshop'
    KIND_NATIONAL_HOLIDAY = 'national_holiday'
    KIND_PUBLIC_HEARING = 'public_hearing'
    KIND_CHOICES = [
        (KIND_ELECTION, 'Election'),
        (KIND_PUBLIC_CONSULTATION, 'Public consultation'),
        (KIND_COMMUNITY_MEETING, 'Community meeting'),
        (KIND_WORKSHOP, 'Civic education workshop'),
        (KIND_NATIONAL_HOLIDAY, 'National holiday'),
        (KIND_PUBLIC_HEARING, 'Public hearing'),
    ]

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    description_ar = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    location_ar = models.CharField(max_length=255, blank=True)
    kind = models.CharField(max_length=32, choices=KIND_CHOICES, db_index=True)
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    is_all_day = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
    )
    allows_registration = models.BooleanField(default=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    source_name = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(blank=True, default='')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='civic_events_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'civic_events'
        ordering = ['starts_at']
        verbose_name = 'civic event'
        verbose_name_plural = 'civic events'

    def __str__(self):
        return self.title

    @property
    def is_cancelled(self) -> bool:
        return self.status == self.STATUS_CANCELLED

    def accepts_registration(self) -> bool:
        if self.status != self.STATUS_PUBLISHED:
            return False
        if self.kind == self.KIND_NATIONAL_HOLIDAY:
            return False
        return self.allows_registration


class EventSignup(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(CivicEvent, on_delete=models.CASCADE, related_name='signups')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='event_signups',
    )
    is_registered = models.BooleanField(default=False)
    reminder_enabled = models.BooleanField(default=False, db_index=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event_signups'
        unique_together = [('organization', 'event', 'user')]
        indexes = [
            models.Index(fields=['reminder_enabled', 'reminder_sent_at']),
        ]

    def __str__(self):
        return f'{self.user_id} · {self.event_id}'
