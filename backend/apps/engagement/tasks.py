from celery import shared_task

from .reminders import send_due_event_reminders as _send_due_event_reminders


@shared_task(ignore_result=True)
def send_due_event_reminders(window_hours: int = 24) -> int:
    from datetime import timedelta

    return _send_due_event_reminders(window=timedelta(hours=window_hours))
