"""HTTP helpers that reject non-http(s) URL schemes before urlopen (Bandit B310)."""

from __future__ import annotations

import urllib.parse
import urllib.request
from typing import Any


def assert_http_url(url: str, *, allow_http: bool = True) -> str:
    """Raise ValueError unless *url* uses an allowed scheme and has a host."""
    parsed = urllib.parse.urlparse(url)
    allowed = {'http', 'https'} if allow_http else {'https'}
    if parsed.scheme not in allowed or not parsed.netloc:
        schemes = ', '.join(sorted(allowed))
        raise ValueError(f'URL must use {schemes} with a host: {url!r}')
    return url


def safe_urlopen(
    url_or_request: str | urllib.request.Request,
    *,
    timeout: float = 10,
    allow_http: bool = False,
) -> Any:
    """urlopen after validating the target scheme (https by default)."""
    if isinstance(url_or_request, urllib.request.Request):
        assert_http_url(url_or_request.full_url, allow_http=allow_http)
        request: str | urllib.request.Request = url_or_request
    else:
        assert_http_url(url_or_request, allow_http=allow_http)
        request = url_or_request
    # Scheme validated above; urlopen is otherwise the stdlib HTTP client.
    return urllib.request.urlopen(request, timeout=timeout)  # nosec B310
