import io
import json
import urllib.error
from unittest.mock import patch

import pytest
from django.core.mail import send_mail
from django.test import override_settings

from apps.core.brevo_mail import BREVO_SMTP_EMAIL_URL, RENDER_BREVO_API_HINT
from apps.core.tasks import format_mail_error


class _OkResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return b'{"messageId":"abc-123"}'


@override_settings(
    EMAIL_BACKEND='apps.core.brevo_mail.BrevoAPIEmailBackend',
    BREVO_API_KEY='xkeysib-test',
    DEFAULT_FROM_EMAIL='sender@example.com',
)
def test_brevo_backend_posts_to_https_api():
    captured = {}

    def fake_urlopen(request, timeout=None):
        captured['url'] = request.full_url
        captured['timeout'] = timeout
        captured['body'] = json.loads(request.data.decode())
        captured['api_key'] = request.get_header('Api-key')
        return _OkResponse()

    with patch('apps.core.brevo_mail.urllib.request.urlopen', side_effect=fake_urlopen):
        sent = send_mail('Verify', 'Click here', None, ['user@example.com'], fail_silently=False)

    assert sent == 1
    assert captured['url'] == BREVO_SMTP_EMAIL_URL
    assert captured['timeout'] == 15
    assert captured['api_key'] == 'xkeysib-test'
    assert captured['body']['sender']['email'] == 'sender@example.com'
    assert captured['body']['to'] == [{'email': 'user@example.com'}]
    assert captured['body']['subject'] == 'Verify'
    assert captured['body']['textContent'] == 'Click here'


@override_settings(
    EMAIL_BACKEND='apps.core.brevo_mail.BrevoAPIEmailBackend',
    BREVO_API_KEY='',
    DEFAULT_FROM_EMAIL='sender@example.com',
)
def test_brevo_backend_requires_api_key():
    with pytest.raises(RuntimeError, match='BREVO_API_KEY'):
        send_mail('Verify', 'Body', None, ['user@example.com'], fail_silently=False)


@override_settings(
    EMAIL_BACKEND='apps.core.brevo_mail.BrevoAPIEmailBackend',
    BREVO_API_KEY='xkeysib-test',
    DEFAULT_FROM_EMAIL='sender@example.com',
)
def test_brevo_backend_surfaces_http_errors():
    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url,
            401,
            'Unauthorized',
            hdrs=None,
            fp=io.BytesIO(b'{"message":"Key not found"}'),
        )

    with patch('apps.core.brevo_mail.urllib.request.urlopen', side_effect=fake_urlopen):
        with pytest.raises(RuntimeError, match='401'):
            send_mail('Verify', 'Body', None, ['user@example.com'], fail_silently=False)


def test_format_mail_error_explains_render_smtp_timeout():
    text = format_mail_error(OSError(110, 'Connection timed out'))
    assert 'timed out' in text.lower() or '110' in text
    assert 'BREVO_API_KEY' in text
    assert RENDER_BREVO_API_HINT.split()[0] in text
