from .models import Notification


def notify_user(user, notification_type, title, message):
    """Create a single notification for one user (cheap, stays inline)."""
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
    )
    from .push_services import send_push_to_user

    send_push_to_user(user, title, message)


def notify_all_users(notification_type, title, message, organization_id=None):
    """Fan out a notification to all active users via a background task.

    When ``organization_id`` is given, only members of that organization are
    notified (tenant isolation). Enqueues the work so request handlers (e.g.
    publishing an article) return immediately regardless of user count. With
    CELERY_TASK_ALWAYS_EAGER (dev/test) this still runs inline.
    """
    from .tasks import broadcast_notification_task

    broadcast_notification_task.delay(notification_type, title, message, organization_id)
