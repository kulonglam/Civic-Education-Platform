import json
import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_push_to_user(user, title: str, message: str) -> int:
    """Send a web push to all subscriptions for a user. Returns count sent."""
    public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
    private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
    if not public_key or not private_key:
        return 0

    from .models import WebPushSubscription

    subscriptions = WebPushSubscription.objects.filter(user=user)
    if not subscriptions.exists():
        return 0

    try:
        from pywebpush import WebPushException, webpush
    except ImportError:
        logger.warning('pywebpush not installed; skipping web push delivery')
        return 0

    payload = json.dumps({'title': title, 'body': message})
    sent = 0
    stale = []

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {'p256dh': sub.p256dh, 'auth': sub.auth},
                },
                data=payload,
                vapid_private_key=private_key,
                vapid_claims={'sub': settings.VAPID_ADMIN_EMAIL},
            )
            sent += 1
        except WebPushException as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            if status in (404, 410):
                stale.append(sub.id)
            logger.warning('Web push failed for %s: %s', sub.id, exc)

    if stale:
        WebPushSubscription.objects.filter(id__in=stale).delete()

    return sent


def push_subscription_stats() -> dict:
    from django.contrib.auth import get_user_model
    from django.db.models import Count

    from .models import WebPushSubscription

    User = get_user_model()
    total = WebPushSubscription.objects.count()
    users_with_push = WebPushSubscription.objects.values('user_id').distinct().count()
    inactive_user_subscriptions = WebPushSubscription.objects.filter(user__is_active=False).count()
    top_users = list(
        WebPushSubscription.objects.values('user__email')
        .annotate(subscriptions=Count('id'))
        .order_by('-subscriptions')[:5]
    )
    return {
        'total_subscriptions': total,
        'users_with_push': users_with_push,
        'inactive_user_subscriptions': inactive_user_subscriptions,
        'total_users': User.objects.filter(is_active=True).count(),
        'top_users': top_users,
    }


def cleanup_push_subscriptions(*, max_age_days: int = 180) -> dict:
    from datetime import timedelta

    from django.utils import timezone

    from .models import WebPushSubscription

    deleted_inactive = WebPushSubscription.objects.filter(user__is_active=False).delete()[0]
    cutoff = timezone.now() - timedelta(days=max_age_days)
    deleted_old = WebPushSubscription.objects.filter(created_at__lt=cutoff).delete()[0]
    return {
        'deleted_inactive_user': deleted_inactive,
        'deleted_older_than_days': deleted_old,
        'max_age_days': max_age_days,
    }
