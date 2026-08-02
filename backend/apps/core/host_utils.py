"""Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists."""

from __future__ import annotations

import os
from urllib.parse import urlparse


def unique_hosts(*values: str) -> list[str]:
    """Split comma-separated host strings and return de-duplicated hosts."""
    hosts: list[str] = []
    for value in values:
        for part in value.split(','):
            host = part.strip()
            if host and host not in hosts:
                hosts.append(host)
    return hosts


def render_hostname() -> str:
    """Return the Render service hostname from platform-injected env vars."""
    host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
    if host:
        return host
    url = os.environ.get('RENDER_EXTERNAL_URL', '').strip()
    if not url:
        return ''
    return (urlparse(url).hostname or '').strip()


def redis_url_points_to_localhost(url: str) -> bool:
    """True when a Redis URL targets this machine (dev default, invalid on Render)."""
    if not url:
        return False
    host = (urlparse(url.strip()).hostname or '').lower()
    return host in {'localhost', '127.0.0.1', '::1'}
