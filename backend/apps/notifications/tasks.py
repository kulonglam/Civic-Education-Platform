import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Notification, SmsMessage
from .sms_services import deliver_sms, org_member_phones, send_sms_to_phone

logger = logging.getLogger(__name__)

BATCH_SIZE = 500


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def broadcast_notification_task(
    self,
    notification_type: str,
    title: str,
    message: str,
    organization_id: str | None = None,
):
    """Fan out an in-app notification to active users in batches."""
    User = get_user_model()
    users = User.objects.filter(is_active=True)
    if organization_id is not None:
        users = users.filter(memberships__organization_id=organization_id)
    user_ids = users.values_list('id', flat=True).distinct().iterator()

    batch: list[Notification] = []
    total = 0
    for user_id in user_ids:
        batch.append(
            Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                organization_id=organization_id,
            )
        )
        if len(batch) >= BATCH_SIZE:
            Notification.objects.bulk_create(batch, batch_size=BATCH_SIZE)
            total += len(batch)
            batch = []
    if batch:
        Notification.objects.bulk_create(batch, batch_size=BATCH_SIZE)
        total += len(batch)

    logger.info('Broadcast notification %r delivered to %d users', title, total)
    return total


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_sms_task(self, sms_log_id: str):
    sms_log = SmsMessage.objects.filter(id=sms_log_id).first()
    if sms_log is None:
        return {'status': 'missing'}
    deliver_sms(sms_log)
    return {'status': sms_log.status, 'phone': sms_log.phone}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def broadcast_sms_task(self, message: str, organization_id: str):
    from apps.tenants.models import Organization

    organization = Organization.objects.filter(id=organization_id).first()
    if organization is None:
        return {'status': 'missing_org'}

    sent = 0
    failed = 0
    for user in org_member_phones(organization):
        sms_log = send_sms_to_phone(
            user.phone,
            message,
            message_type=SmsMessage.TYPE_BROADCAST,
            user=user,
            organization=organization,
        )
        if sms_log.status == SmsMessage.STATUS_SENT:
            sent += 1
        else:
            failed += 1

    logger.info(
        'SMS broadcast for org %s: sent=%d failed=%d',
        organization.slug,
        sent,
        failed,
    )
    return {'sent': sent, 'failed': failed}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_whatsapp_task(self, log_id: str):
    from .models import WhatsAppMessage
    from .whatsapp_services import deliver_whatsapp

    log = WhatsAppMessage.objects.filter(id=log_id).first()
    if log is None:
        return {'status': 'missing'}
    deliver_whatsapp(log)
    return {'status': log.status, 'phone': log.phone}


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def broadcast_whatsapp_task(self, message: str, organization_id: str):
    from apps.tenants.models import Organization
    from .models import WhatsAppMessage
    from .whatsapp_services import org_whatsapp_recipients, send_whatsapp_to_phone

    organization = Organization.objects.filter(id=organization_id).first()
    if organization is None:
        return {'status': 'missing_org'}

    sent = 0
    failed = 0
    for user in org_whatsapp_recipients(organization):
        log = send_whatsapp_to_phone(
            user.phone,
            message,
            message_type=WhatsAppMessage.TYPE_BROADCAST,
            user=user,
            organization=organization,
        )
        if log.status == WhatsAppMessage.STATUS_SENT:
            sent += 1
        else:
            failed += 1
    logger.info(
        'WhatsApp broadcast for org %s: sent=%d failed=%d',
        organization.slug,
        sent,
        failed,
    )
    return {'sent': sent, 'failed': failed}


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def cleanup_push_subscriptions_task(self, max_age_days: int = 180):
    from .push_services import cleanup_push_subscriptions

    return cleanup_push_subscriptions(max_age_days=max_age_days)
