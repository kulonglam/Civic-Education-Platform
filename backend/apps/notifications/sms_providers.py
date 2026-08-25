import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)


class SmsSendResult:
    def __init__(self, success: bool, reference: str = '', error: str = ''):
        self.success = success
        self.reference = reference
        self.error = error


class BaseSmsProvider:
    def send(self, phone: str, message: str) -> SmsSendResult:
        raise NotImplementedError


class DummySmsProvider(BaseSmsProvider):
    """Log SMS in development; always succeeds."""

    def send(self, phone: str, message: str) -> SmsSendResult:
        logger.info('[dummy-sms] to=%s message=%s', phone, message[:120])
        return SmsSendResult(success=True, reference='dummy-sms-id')


class AfricasTalkingSmsProvider(BaseSmsProvider):
    def __init__(self):
        import africastalking

        africastalking.initialize(
            username=settings.AT_USERNAME,
            api_key=settings.AT_API_KEY,
        )
        self._sms = africastalking.SMS

    def send(self, phone: str, message: str) -> SmsSendResult:
        sender_id = settings.AT_SENDER_ID or None
        try:
            response = self._sms.send(message, [phone], sender_id)
            recipients = (response or {}).get('SMSMessageData', {}).get('Recipients', [])
            if not recipients:
                return SmsSendResult(success=False, error='No recipients in provider response.')
            recipient = recipients[0]
            status_code = str(recipient.get('statusCode'))
            if status_code in ('101', '102'):
                return SmsSendResult(
                    success=True,
                    reference=str(recipient.get('messageId', '')),
                )
            return SmsSendResult(
                success=False,
                error=recipient.get('status') or f'Status code {status_code}',
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception('Africa\'s Talking SMS failed: %s', exc)
            return SmsSendResult(success=False, error=str(exc))


def get_sms_provider() -> BaseSmsProvider:
    provider = getattr(settings, 'SMS_PROVIDER', 'dummy')
    if provider == 'africastalking' and settings.AT_API_KEY and settings.AT_USERNAME:
        return AfricasTalkingSmsProvider()
    return DummySmsProvider()


def normalize_phone(raw: str) -> str:
    """Normalize to E.164 for Uganda (+256)."""
    if not raw:
        raise ValueError('Phone number is required.')
    cleaned = re.sub(r'[\s\-()]', '', raw.strip())
    if cleaned.startswith('+'):
        digits = cleaned[1:]
    else:
        digits = cleaned
    digits = re.sub(r'\D', '', digits)
    if digits.startswith('256'):
        national = digits[3:]
    elif digits.startswith('0'):
        national = digits[1:]
    else:
        national = digits
    if national.startswith('0'):
        national = national[1:]
    if not national.isdigit() or len(national) != 9 or national[0] not in '37':
        raise ValueError('Enter a valid Uganda mobile number (e.g. +256772123456).')
    return f'+256{national}'
