import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_email_task(self, subject: str, message: str, recipients: list[str]):
    """Send an email asynchronously with retry and logging.

    Replaces fail_silently so delivery failures are observable and retried
    instead of being swallowed.
    """
    sent = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=False,
    )
    logger.info('Email sent: subject=%r recipients=%s result=%s', subject, recipients, sent)
    return sent
