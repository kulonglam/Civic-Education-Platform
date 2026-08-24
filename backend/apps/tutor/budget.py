"""Daily message quota for the AI tutor.

Usage is counted in Redis for speed and written through to ``TutorDailyUsage``
so the count survives cache eviction and process restarts.
"""

from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone

from apps.billing.services import get_active_plan
from apps.tenants.context import get_current_organization
from apps.tenants.services import get_user_organization

from .exceptions import TutorBudgetExceeded
from .models import TutorDailyUsage

DEFAULT_DAILY_LIMIT = 30


def _daily_cache_key(user_id) -> str:
    today = timezone.localdate().isoformat()
    return f'tutor:daily:{user_id}:{today}'


def _seconds_until_midnight() -> int:
    now = timezone.localtime()
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(int((tomorrow - now).total_seconds()), 60)


def get_daily_limit(user) -> int | None:
    organization = get_current_organization() or get_user_organization(user)
    plan = get_active_plan(organization) if organization else None
    if plan is None:
        return DEFAULT_DAILY_LIMIT
    limit = (plan.features or {}).get('tutor_daily_messages', DEFAULT_DAILY_LIMIT)
    if limit in (None, '', 'unlimited'):
        return None
    return int(limit)


def get_daily_usage(user) -> int:
    """Return today's usage from Redis cache, seeding from DB on cold miss."""
    key = _daily_cache_key(user.pk)
    cached = cache.get(key)
    if cached is not None:
        return int(cached)
    # Cold miss: read from DB to avoid double-counting across restarts
    today = timezone.localdate()
    row = TutorDailyUsage.objects.filter(user=user, date=today).first()
    count = row.message_count if row else 0
    cache.set(key, count, timeout=_seconds_until_midnight())
    return count


def increment_daily_usage(user) -> int:
    """Increment Redis counter and persist to DB asynchronously."""
    key = _daily_cache_key(user.pk)
    try:
        new_val = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=_seconds_until_midnight())
        new_val = 1
    # Write-through to DB using upsert so the counter survives cache eviction
    today = timezone.localdate()
    TutorDailyUsage.objects.update_or_create(
        user=user,
        date=today,
        defaults={'message_count': new_val},
    )
    return new_val


def enforce_budget(user) -> None:
    limit = get_daily_limit(user)
    if limit is None:
        return
    if get_daily_usage(user) >= limit:
        raise TutorBudgetExceeded(
            detail=f'Daily limit of {limit} tutor messages reached. Try again tomorrow or upgrade your plan.'
        )
