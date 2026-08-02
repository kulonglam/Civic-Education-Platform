"""Helpers for building Django ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS lists."""


def unique_hosts(*values: str) -> list[str]:
    """Split comma-separated host strings and return de-duplicated hosts."""
    hosts: list[str] = []
    for value in values:
        for part in value.split(','):
            host = part.strip()
            if host and host not in hosts:
                hosts.append(host)
    return hosts
