from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tenants.context import get_current_organization

from .models import WhatsAppMessage
from .sms_services import org_member_phones
from .whatsapp_providers import get_whatsapp_provider, whatsapp_to_e164

User = get_user_model()


def create_whatsapp_log(
    *,
    phone: str,
    message: str,
    message_type: str,
    user=None,
    organization=None,
    direction=WhatsAppMessage.DIRECTION_OUTBOUND,
) -> WhatsAppMessage:
    if organization is None:
        organization = get_current_organization()
    if organization is None and user is not None:
        from apps.tenants.models import Membership

        membership = (
            Membership.objects.filter(user=user, organization__is_active=True)
            .select_related('organization')
            .order_by('created_at')
            .first()
        )
        organization = membership.organization if membership else None
    return WhatsAppMessage.objects.create(
        user=user,
        organization=organization,
        phone=phone,
        message=message,
        message_type=message_type,
        direction=direction,
        status=WhatsAppMessage.STATUS_PENDING,
    )


def deliver_whatsapp(log: WhatsAppMessage) -> WhatsAppMessage:
    provider = get_whatsapp_provider()
    result = provider.send(log.phone, log.message)
    if result.success:
        log.status = WhatsAppMessage.STATUS_SENT
        log.provider_reference = result.reference
        log.sent_at = timezone.now()
        log.error_detail = ''
    else:
        log.status = WhatsAppMessage.STATUS_FAILED
        log.error_detail = result.error
    log.save(update_fields=['status', 'provider_reference', 'sent_at', 'error_detail'])
    return log


def queue_whatsapp_to_phone(
    phone: str,
    message: str,
    *,
    message_type=WhatsAppMessage.TYPE_ALERT,
    user=None,
    organization=None,
) -> WhatsAppMessage:
    normalized = whatsapp_to_e164(phone)
    log = create_whatsapp_log(
        phone=normalized,
        message=message,
        message_type=message_type,
        user=user,
        organization=organization,
    )
    from .tasks import send_whatsapp_task

    send_whatsapp_task.delay(str(log.id))
    return log


def send_whatsapp_to_phone(
    phone: str,
    message: str,
    *,
    message_type=WhatsAppMessage.TYPE_ALERT,
    user=None,
    organization=None,
) -> WhatsAppMessage:
    normalized = whatsapp_to_e164(phone)
    log = create_whatsapp_log(
        phone=normalized,
        message=message,
        message_type=message_type,
        user=user,
        organization=organization,
    )
    return deliver_whatsapp(log)


def send_whatsapp_to_user(user, message: str, *, organization=None) -> WhatsAppMessage | None:
    if not user.phone:
        return None
    return send_whatsapp_to_phone(
        user.phone,
        message,
        message_type=WhatsAppMessage.TYPE_ALERT,
        user=user,
        organization=organization,
    )


def record_inbound_whatsapp(*, phone: str, message: str, provider_reference: str = '') -> WhatsAppMessage | None:
    try:
        normalized = whatsapp_to_e164(phone)
    except ValueError:
        return None
    user = User.objects.filter(phone=normalized, is_active=True).first()
    organization = None
    if user is not None:
        from apps.tenants.models import Membership

        membership = (
            Membership.objects.filter(user=user, organization__is_active=True)
            .select_related('organization')
            .order_by('created_at')
            .first()
        )
        organization = membership.organization if membership else None
    if organization is None:
        return None
    log = WhatsAppMessage.all_objects.create(
        user=user,
        organization=organization,
        phone=normalized,
        message=message,
        message_type=WhatsAppMessage.TYPE_INBOUND,
        direction=WhatsAppMessage.DIRECTION_INBOUND,
        status=WhatsAppMessage.STATUS_SENT,
        provider_reference=provider_reference,
        sent_at=timezone.now(),
    )
    return log


def org_whatsapp_recipients(organization):
    return org_member_phones(organization)
