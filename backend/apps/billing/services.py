from django.apps import apps as django_apps
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException

from .models import Plan, Subscription

_QUOTA_CACHE_TTL = 60  # seconds; short-lived so real-time enforcement stays accurate


class QuotaExceeded(APIException):
    status_code = 402  # Payment Required
    default_detail = 'Plan quota exceeded. Upgrade your plan to continue.'
    default_code = 'quota_exceeded'


class AnalyticsNotAvailable(APIException):
    status_code = 402
    default_detail = 'Analytics requires a Pro or Enterprise plan. Upgrade to access reports.'
    default_code = 'analytics_not_available'


def get_default_plan() -> Plan | None:
    return Plan.objects.filter(code=Plan.FREE).first() or Plan.objects.filter(is_active=True).first()


def get_subscription(organization) -> Subscription | None:
    return Subscription.objects.filter(organization=organization).select_related('plan').first()


def ensure_subscription(organization) -> Subscription | None:
    """Return the org subscription, creating a free-plan row if missing."""
    subscription = get_subscription(organization)
    if subscription is not None:
        return subscription
    plan = get_default_plan()
    if plan is None:
        return None
    return Subscription.objects.create(
        organization=organization,
        plan=plan,
        status=Subscription.ACTIVE,
    )


def plan_code_for_stripe_price(price_id: str) -> str | None:
    if not price_id:
        return None
    for code, configured in getattr(settings, 'STRIPE_PRICE_IDS', {}).items():
        if configured and configured == price_id:
            return code
    return None


def get_active_plan(organization) -> Plan | None:
    subscription = get_subscription(organization)
    if subscription and subscription.is_current:
        return subscription.plan
    return get_default_plan()


# Maps a quota resource name to its (app_label, model) for usage counting.
_RESOURCE_MODELS = {
    'members': ('tenants', 'Membership'),
    'articles': ('learning', 'Article'),
    'quizzes': ('quizzes', 'Quiz'),
}


def count_usage(organization, resource: str) -> int:
    cache_key = f'quota:{organization.pk}:{resource}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached
    app_label, model_name = _RESOURCE_MODELS[resource]
    model = django_apps.get_model(app_label, model_name)
    manager = getattr(model, 'all_objects', model.objects)
    count = manager.filter(organization=organization).count()
    cache.set(cache_key, count, timeout=_QUOTA_CACHE_TTL)
    return count


def invalidate_quota_cache(organization, resource: str) -> None:
    """Call after creating/deleting a resource to keep cache consistent."""
    cache.delete(f'quota:{organization.pk}:{resource}')


def check_quota(organization, resource: str) -> None:
    """Raise ``QuotaExceeded`` if creating one more ``resource`` would exceed the plan."""
    plan = get_active_plan(organization)
    if plan is None:
        return
    limit = plan.quota_for(resource)
    if limit is None:  # unlimited
        return
    if count_usage(organization, resource) >= limit:
        raise QuotaExceeded(
            detail=(
                f'Your "{plan.name}" plan allows up to {limit} {resource}. '
                'Upgrade your plan to add more.'
            )
        )


def plan_has_analytics(organization) -> bool:
    plan = get_active_plan(organization)
    if plan is None:
        return False
    return bool((plan.features or {}).get('analytics'))


def require_analytics(organization) -> None:
    if not plan_has_analytics(organization):
        raise AnalyticsNotAvailable()


class SmsNotAvailable(APIException):
    status_code = 402
    default_detail = 'SMS alerts require a Pro or Enterprise plan. Upgrade to send SMS.'
    default_code = 'sms_not_available'


def plan_has_sms(organization) -> bool:
    plan = get_active_plan(organization)
    if plan is None:
        return False
    return bool((plan.features or {}).get('sms_alerts'))


def require_sms(organization) -> None:
    if not plan_has_sms(organization):
        raise SmsNotAvailable()


class SsoNotAvailable(APIException):
    status_code = 402
    default_detail = 'Single sign-on requires an Enterprise plan.'
    default_code = 'sso_not_available'


def plan_has_sso(organization) -> bool:
    plan = get_active_plan(organization)
    if plan is None:
        return False
    return bool((plan.features or {}).get('sso'))


def require_sso(organization) -> None:
    if not plan_has_sso(organization):
        raise SsoNotAvailable()


def usage_summary(organization) -> dict:
    plan = get_active_plan(organization)
    summary = {}
    for resource in _RESOURCE_MODELS:
        limit = plan.quota_for(resource) if plan else None
        summary[resource] = {'used': count_usage(organization, resource), 'limit': limit}
    return summary


def _subscription_for_organization(org_id: str) -> Subscription | None:
    if not org_id:
        return None
    return Subscription.objects.filter(organization_id=org_id).select_related('plan').first()


def _subscription_for_stripe_id(stripe_subscription_id: str) -> Subscription | None:
    if not stripe_subscription_id:
        return None
    return Subscription.objects.filter(
        provider_subscription_id=stripe_subscription_id,
    ).select_related('plan').first()


def _apply_plan_code(subscription: Subscription, plan_code: str | None) -> None:
    if not plan_code:
        return
    plan = Plan.objects.filter(code=plan_code, is_active=True).first()
    if plan:
        subscription.plan = plan


def apply_checkout_completed(session: dict) -> None:
    """Sync subscription after Stripe Checkout completes."""
    metadata = session.get('metadata') or {}
    subscription = _subscription_for_organization(metadata.get('organization_id'))
    if subscription is None:
        return

    _apply_plan_code(subscription, metadata.get('plan_code'))
    subscription.status = Subscription.ACTIVE

    stripe_sub_id = session.get('subscription')
    if stripe_sub_id:
        subscription.provider_subscription_id = stripe_sub_id

    customer_id = session.get('customer')
    if customer_id:
        subscription.provider_customer_id = customer_id

    subscription.save()


def apply_subscription_updated(stripe_subscription: dict) -> None:
    """Sync plan/status when Stripe subscription changes."""
    metadata = stripe_subscription.get('metadata') or {}
    subscription = (
        _subscription_for_organization(metadata.get('organization_id'))
        or _subscription_for_stripe_id(stripe_subscription.get('id'))
    )
    if subscription is None:
        return

    status_map = {
        'active': Subscription.ACTIVE,
        'trialing': Subscription.TRIALING,
        'past_due': Subscription.PAST_DUE,
        'canceled': Subscription.CANCELED,
        'unpaid': Subscription.PAST_DUE,
        'incomplete': Subscription.PAST_DUE,
        'incomplete_expired': Subscription.CANCELED,
    }
    stripe_status = stripe_subscription.get('status')
    if stripe_status in status_map:
        subscription.status = status_map[stripe_status]

    plan_code = metadata.get('plan_code')
    if not plan_code:
        items = (stripe_subscription.get('items') or {}).get('data') or []
        if items:
            price_id = (items[0].get('price') or {}).get('id')
            plan_code = plan_code_for_stripe_price(price_id)
    _apply_plan_code(subscription, plan_code)

    if stripe_subscription.get('id'):
        subscription.provider_subscription_id = stripe_subscription['id']
    if stripe_subscription.get('customer'):
        subscription.provider_customer_id = stripe_subscription['customer']

    subscription.save()


def apply_subscription_deleted(stripe_subscription: dict) -> None:
    """Downgrade to the free plan when a paid subscription ends."""
    metadata = stripe_subscription.get('metadata') or {}
    subscription = (
        _subscription_for_organization(metadata.get('organization_id'))
        or _subscription_for_stripe_id(stripe_subscription.get('id'))
    )
    if subscription is None:
        return

    subscription.status = Subscription.CANCELED
    free_plan = get_default_plan()
    if free_plan:
        subscription.plan = free_plan
    subscription.save()


def self_serve_checkout_enabled() -> bool:
    """Paid self-serve checkout is off when dummy billing is used (East Africa)."""
    return getattr(settings, 'BILLING_PROVIDER', 'dummy') != 'dummy'


def assign_organization_plan(organization, plan: Plan) -> Subscription:
    """Platform-operator plan assignment (invoice / card upgrade)."""
    subscription = ensure_subscription(organization)
    if subscription is None:
        return Subscription.objects.create(
            organization=organization,
            plan=plan,
            status=Subscription.ACTIVE,
        )
    subscription.plan = plan
    subscription.status = Subscription.ACTIVE
    subscription.save(update_fields=['plan', 'status'])
    for resource in _RESOURCE_MODELS:
        invalidate_quota_cache(organization, resource)
    return subscription
