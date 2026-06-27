from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.tenants.models import Organization

from .models import Subscription
from .services import get_default_plan


@receiver(post_save, sender=Organization)
def create_default_subscription(sender, instance, created, **kwargs):
    """Every new organization starts on the default (free) plan."""
    if not created:
        return
    plan = get_default_plan()
    if plan is None:
        return  # plans not seeded yet (e.g. during initial migrate)
    Subscription.objects.get_or_create(
        organization=instance,
        defaults={'plan': plan, 'status': Subscription.ACTIVE},
    )
