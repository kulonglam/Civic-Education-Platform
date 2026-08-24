import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

from .sms_providers import SmsSendResult, normalize_phone

logger = logging.getLogger(__name__)

GRAPH_VERSION = 'v21.0'


class BaseWhatsAppProvider:
    def send(self, phone: str, message: str) -> SmsSendResult:
        raise NotImplementedError


class DummyWhatsAppProvider(BaseWhatsAppProvider):
    """Log WhatsApp messages in development; always succeeds."""

    def send(self, phone: str, message: str) -> SmsSendResult:
        logger.info('[dummy-whatsapp] to=%s message=%s', phone, message[:120])
        return SmsSendResult(success=True, reference='dummy-whatsapp-id')


class MetaCloudWhatsAppProvider(BaseWhatsAppProvider):
    def send(self, phone: str, message: str) -> SmsSendResult:
        token = settings.WHATSAPP_ACCESS_TOKEN
        phone_id = settings.WHATSAPP_PHONE_NUMBER_ID
        url = f'https://graph.facebook.com/{GRAPH_VERSION}/{phone_id}/messages'
        payload = {
            'messaging_product': 'whatsapp',
            'to': phone.lstrip('+'),
            'type': 'text',
            'text': {'preview_url': True, 'body': message},
        }
        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = json.loads(response.read().decode('utf-8') or '{}')
            messages = body.get('messages') or []
            reference = str((messages[0] or {}).get('id', '')) if messages else ''
            return SmsSendResult(success=True, reference=reference)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')[:400]
            logger.warning('WhatsApp Cloud API failed: %s %s', exc.code, detail)
            return SmsSendResult(success=False, error=detail or str(exc))
        except Exception as exc:  # noqa: BLE001
            logger.exception('WhatsApp send failed: %s', exc)
            return SmsSendResult(success=False, error=str(exc))


def whatsapp_cloud_configured() -> bool:
    return bool(settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID)


def get_whatsapp_provider() -> BaseWhatsAppProvider:
    provider = getattr(settings, 'WHATSAPP_PROVIDER', 'dummy')
    if provider == 'meta' and whatsapp_cloud_configured():
        return MetaCloudWhatsAppProvider()
    return DummyWhatsAppProvider()


def whatsapp_to_e164(raw: str) -> str:
    return normalize_phone(raw)
