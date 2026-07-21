import urllib.request

import pytest

from apps.core.safe_http import assert_http_url, safe_urlopen


def test_assert_http_url_allows_https():
    assert assert_http_url('https://idp.example.com/oidc', allow_http=False).startswith('https://')


def test_assert_http_url_rejects_file_scheme():
    with pytest.raises(ValueError, match='https'):
        assert_http_url('file:///etc/passwd', allow_http=False)


def test_assert_http_url_rejects_http_when_https_required():
    with pytest.raises(ValueError, match='https'):
        assert_http_url('http://idp.example.com', allow_http=False)


def test_assert_http_url_allows_http_for_smoke():
    assert assert_http_url('http://127.0.0.1:8000', allow_http=True)


def test_safe_urlopen_rejects_before_network(monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError('urlopen should not be called for invalid schemes')

    monkeypatch.setattr(urllib.request, 'urlopen', boom)
    with pytest.raises(ValueError):
        safe_urlopen('file:///tmp/x', allow_http=True)
