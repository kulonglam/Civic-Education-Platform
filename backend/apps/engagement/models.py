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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=500)
    question_ar = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
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
