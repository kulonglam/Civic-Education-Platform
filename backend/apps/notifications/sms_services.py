import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.models import PhoneOTP
from apps.tenants.context import get_current_organization

from .models import SmsMessage
from .sms_providers import get_sms_provider, normalize_phone

User = get_user_model()
OTP_TTL_MINUTES = 10


def create_sms_log(
    *,
    phone: str,
    message: str,
    message_type: str,
    user=None,
    organization=None,
) -> SmsMessage:
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
    return SmsMessage.objects.create(
        user=user,
        organization=organization,
        phone=phone,
        message=message,
        message_type=message_type,
        status=SmsMessage.STATUS_PENDING,
    )


def deliver_sms(sms_log: SmsMessage) -> SmsMessage:
    provider = get_sms_provider()
    result = provider.send(sms_log.phone, sms_log.message)
    if result.success:
        sms_log.status = SmsMessage.STATUS_SENT
        sms_log.provider_reference = result.reference
        sms_log.sent_at = timezone.now()
        sms_log.error_detail = ''
    else:
        sms_log.status = SmsMessage.STATUS_FAILED
        sms_log.error_detail = result.error
    sms_log.save(
        update_fields=['status', 'provider_reference', 'sent_at', 'error_detail'],
    )
    return sms_log


def queue_sms_to_phone(
    phone: str,
    message: str,
    *,
    message_type=SmsMessage.TYPE_SMS,
    user=None,
    organization=None,
) -> SmsMessage:
    normalized = normalize_phone(phone)
    sms_log = create_sms_log(
        phone=normalized,
        message=message,
        message_type=message_type,
        user=user,
        organization=organization,
    )
    from .tasks import send_sms_task

    send_sms_task.delay(str(sms_log.id))
    return sms_log


def send_sms_to_phone(
    phone: str,
    message: str,
    *,
    message_type=SmsMessage.TYPE_SMS,
    user=None,
    organization=None,
) -> SmsMessage:
    normalized = normalize_phone(phone)
    sms_log = create_sms_log(
        phone=normalized,
        message=message,
        message_type=message_type,
        user=user,
        organization=organization,
    )
    return deliver_sms(sms_log)


def send_sms_to_user(user, message: str, *, message_type=SmsMessage.TYPE_SMS) -> SmsMessage | None:
    if not user.phone:
        return None
    return send_sms_to_phone(
        user.phone,
        message,
        message_type=message_type,
        user=user,
    )


def issue_phone_otp(user, phone: str, purpose: str) -> PhoneOTP:
    normalized = normalize_phone(phone)
    PhoneOTP.objects.filter(user=user, purpose=purpose, used=False).update(used=True)
    code = f'{secrets.randbelow(1_000_000):06d}'
    return PhoneOTP.objects.create(
        user=user,
        phone=normalized,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
    )


def send_password_reset_otp(user) -> SmsMessage | None:
    if not user.phone:
        return None
    otp = issue_phone_otp(user, user.phone, PhoneOTP.PURPOSE_RESET)
    message = (
        f'Your Civic Education Platform password reset code is {otp.code}. '
        f'It expires in {OTP_TTL_MINUTES} minutes.'
    )
    return queue_sms_to_phone(
        otp.phone,
        message,
        message_type=SmsMessage.TYPE_OTP,
        user=user,
    )


def send_phone_verify_otp(user) -> SmsMessage | None:
    if not user.phone:
        return None
    otp = issue_phone_otp(user, user.phone, PhoneOTP.PURPOSE_VERIFY)
    message = (
        f'Your Civic Education Platform verification code is {otp.code}. '
        f'It expires in {OTP_TTL_MINUTES} minutes.'
    )
    return queue_sms_to_phone(
        otp.phone,
        message,
        message_type=SmsMessage.TYPE_OTP,
        user=user,
    )


def verify_phone_otp(*, phone: str, code: str, purpose: str) -> PhoneOTP:
    normalized = normalize_phone(phone)
    otp = (
        PhoneOTP.objects.filter(
            phone=normalized,
            code=code,
            purpose=purpose,
            used=False,
            expires_at__gt=timezone.now(),
        )
        .select_related('user')
        .first()
    )
    if otp is None:
        raise ValueError('Invalid or expired verification code.')
    otp.used = True
    otp.save(update_fields=['used'])
    return otp


def org_member_phones(organization):
    return (
        User.objects.filter(
            memberships__organization=organization,
            is_active=True,
        )
        .exclude(phone__isnull=True)
        .exclude(phone='')
        .distinct()
    )
