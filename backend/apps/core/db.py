"""IP allowlist helpers and read-replica database router."""

from __future__ import annotations

import ipaddress

from django.conf import settings


def client_ip_from_request(request) -> str | None:
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip() or None
    return request.META.get('REMOTE_ADDR') or None


def ip_allowed(client_ip: str | None, allowlist: list | None) -> bool:
    """Return True when allowlist is empty or client_ip matches an entry."""
    if not allowlist:
        return True
    if not client_ip:
        return False
    try:
        addr = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    for entry in allowlist:
        if not entry:
            continue
        try:
            if '/' in str(entry):
                if addr in ipaddress.ip_network(str(entry), strict=False):
                    return True
            elif addr == ipaddress.ip_address(str(entry)):
                return True
        except ValueError:
            continue
    return False


class ReadReplicaRouter:
    """Route reads to DATABASES['replica'] when configured."""

    def db_for_read(self, model, **hints):
        if 'replica' in getattr(settings, 'DATABASES', {}):
            return 'replica'
        return 'default'

    def db_for_write(self, model, **hints):
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default'
