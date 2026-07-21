"""Unit tests for sanitize helpers and remaining safe_http paths."""

import urllib.request

import pytest

from apps.core.safe_http import assert_http_url, safe_urlopen
from apps.core.sanitize import reject_dangerous_markdown


def test_reject_dangerous_markdown_script():
    with pytest.raises(ValueError):
        reject_dangerous_markdown('Hello <script>alert(1)</script>')


def test_reject_dangerous_markdown_allows_safe():
    assert reject_dangerous_markdown('**Bold** and [link](https://example.com)') is None


def test_safe_urlopen_with_request_object(monkeypatch):
    seen = {}

    class FakeResp:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"ok": true}'

    def fake_urlopen(req, timeout=10):
        seen['url'] = req.full_url if hasattr(req, 'full_url') else req
        seen['timeout'] = timeout
        return FakeResp()

    monkeypatch.setattr(urllib.request, 'urlopen', fake_urlopen)
    req = urllib.request.Request('https://example.com/api', method='GET')
    with safe_urlopen(req, timeout=5, allow_http=False) as resp:
        assert resp.read() == b'{"ok": true}'
    assert seen['url'] == 'https://example.com/api'
    assert seen['timeout'] == 5


def test_assert_http_url_rejects_empty_host():
    with pytest.raises(ValueError):
        assert_http_url('https:///no-host', allow_http=False)
