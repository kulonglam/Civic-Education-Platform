import uuid

from django.db import models

from apps.tenants.models import Organization

UNLIMITED = None


class Plan(models.Model):
    """A subscription tier with pricing and per-tenant quotas."""

    FREE = 'free'
    PRO = 'pro'
    ENTERPRISE = 'enterprise'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='USD')
    interval = models.CharField(max_length=10, default='month')

    # Quotas. NULL means unlimited.
    max_members = models.PositiveIntegerField(null=True, blank=True)
    max_articles = models.PositiveIntegerField(null=True, blank=True)
    max_quizzes = models.PositiveIntegerField(null=True, blank=True)

    features = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'billing_plans'
        ordering = ['sort_order', 'price_cents']

    def __str__(self):
        return self.name

    def quota_for(self, resource: str):
        return getattr(self, f'max_{resource}', None)


class Subscription(models.Model):
    ACTIVE = 'active'
    TRIALING = 'trialing'
    PAST_DUE = 'past_due'
    CANCELED = 'canceled'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (TRIALING, 'Trialing'),
        (PAST_DUE, 'Past Due'),
        (CANCELED, 'Canceled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    provider_customer_id = models.CharField(max_length=255, blank=True)
    provider_subscription_id = models.CharField(max_length=255, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    cancel_at_period_end = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'billing_subscriptions'

    def __str__(self):
        return f'{self.organization.name} - {self.plan.code} ({self.status})'

    @property
    def is_current(self) -> bool:
        return self.status in (self.ACTIVE, self.TRIALING)
