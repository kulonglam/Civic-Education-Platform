"""Django email backend that sends via Brevo's HTTPS API (port 443).

Render free web services block outbound SMTP (ports 25, 465, 587), which
surfaces as ``[Errno 110] Connection timed out``. The REST API is not blocked.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from email.utils import parseaddr

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_SMTP_EMAIL_URL = 'https://api.brevo.com/v3/smtp/email'
_REQUEST_TIMEOUT = 15

RENDER_BREVO_API_HINT = (
    'Render free web services block SMTP ports 25/465/587. '
    'Set BREVO_API_KEY from Brevo → SMTP & API → API Keys '
    '(not the SMTP key) on the API service, then redeploy. '
    'DEFAULT_FROM_EMAIL must be a verified sender.'
)


def _contacts(addresses: list[str]) -> list[dict[str, str]]:
    contacts = []
    for raw in addresses or []:
        name, email = parseaddr(raw)
        if not email:
            continue
        item = {'email': email}
        if name:
            item['name'] = name
        contacts.append(item)
    return contacts


def _html_body(message) -> str:
    for alt, mimetype in getattr(message, 'alternatives', None) or []:
        if mimetype == 'text/html' and alt:
            return alt
    return ''


class BrevoAPIEmailBackend(BaseEmailBackend):
    """POST each message to ``https://api.brevo.com/v3/smtp/email``."""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        api_key = (getattr(settings, 'BREVO_API_KEY', '') or '').strip()
        if not api_key:
            raise RuntimeError(RENDER_BREVO_API_HINT)
        sent = 0
        for message in email_messages:
            self._send_one(message, api_key)
            sent += 1
        return sent

    def _send_one(self, message, api_key: str) -> None:
        name, email = parseaddr(message.from_email or settings.DEFAULT_FROM_EMAIL)
        if not email:
            raise RuntimeError('DEFAULT_FROM_EMAIL is empty; set a Brevo-verified sender.')
        sender = {'email': email}
        if name:
            sender['name'] = name
        to = _contacts(message.to)
        if not to:
            raise RuntimeError('No recipient address for transactional email.')
        payload = {
            'sender': sender,
            'to': to,
            'subject': message.subject or '(no subject)',
            'textContent': message.body or ' ',
        }
        html = _html_body(message)
        if html:
            payload['htmlContent'] = html
        cc = _contacts(getattr(message, 'cc', None) or [])
        if cc:
            payload['cc'] = cc
        bcc = _contacts(getattr(message, 'bcc', None) or [])
        if bcc:
            payload['bcc'] = bcc

        request = urllib.request.Request(
            BREVO_SMTP_EMAIL_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'accept': 'application/json',
                'content-type': 'application/json',
                'api-key': api_key,
            },
            method='POST',
        )
        try:
            with urllib.request.urlopen(request, timeout=_REQUEST_TIMEOUT) as response:
                body = response.read().decode('utf-8', errors='replace')
                logger.info('Brevo API accepted mail: %s', body[:200])
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'Brevo API HTTP {exc.code}: {detail[:400]}') from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f'Brevo API request failed: {exc.reason}') from exc
