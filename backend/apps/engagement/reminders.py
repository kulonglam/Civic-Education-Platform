"""Due-soon reminders for civic events."""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.notifications.fan_out import notify_user

from .models import CivicEvent, EventSignup

REMINDER_WINDOW = timedelta(hours=24)
REMINDER_GRACE = timedelta(hours=1)


def due_signups_qs(now=None, window=REMINDER_WINDOW):
    now = now or timezone.now()
    return EventSignup.objects.filter(
        reminder_enabled=True,
        reminder_sent_at__isnull=True,
        event__status=CivicEvent.STATUS_PUBLISHED,
        event__starts_at__gte=now - REMINDER_GRACE,
        event__starts_at__lte=now + window,
    ).select_related('event', 'user', 'organization')


def event_is_due_for_reminder(event, now=None) -> bool:
    now = now or timezone.now()
    if event.status != CivicEvent.STATUS_PUBLISHED:
        return False
    return now - REMINDER_GRACE <= event.starts_at <= now + REMINDER_WINDOW


def send_event_reminder(signup: EventSignup, *, now=None) -> bool:
    now = now or timezone.now()
    event = signup.event
    if not signup.reminder_enabled or signup.reminder_sent_at or not event_is_due_for_reminder(event, now):
        return False
    updated = EventSignup.objects.filter(
        pk=signup.pk,
        reminder_enabled=True,
        reminder_sent_at__isnull=True,
    ).update(reminder_sent_at=now)
    if not updated:
        return False
    when = timezone.localtime(event.starts_at).strftime('%d %b %Y %H:%M')
    notify_user(
        user=signup.user,
        notification_type='event_reminder',
        title=f'Coming up: {event.title}',
        message=f'{event.title} starts {when}. Add it to your calendar or review the details on the events page.',
        organization=signup.organization,
    )
    signup.reminder_sent_at = now
    return True


def send_due_event_reminders(*, window=REMINDER_WINDOW) -> int:
    sent = 0
    now = timezone.now()
    for signup in due_signups_qs(now=now, window=window):
        if send_event_reminder(signup, now=now):
            sent += 1
    return sent
