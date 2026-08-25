"""Per-request tenant context.

The current organization is stored in a context variable so tenant-scoped
model managers can filter automatically without threading the tenant through
every call. It is set by ``TenantMiddleware`` and cleared at the end of each
request.
"""

from contextlib import contextmanager
from contextvars import ContextVar

_current_organization: ContextVar = ContextVar('current_organization', default=None)
_fail_closed: ContextVar[bool] = ContextVar('tenant_fail_closed', default=False)


def set_current_organization(organization):
    return _current_organization.set(organization)


def get_current_organization():
    return _current_organization.get()


def clear_current_organization(token=None):
    if token is not None:
        _current_organization.reset(token)
    else:
        _current_organization.set(None)


def set_tenant_fail_closed(enabled: bool):
    return _fail_closed.set(enabled)


def reset_tenant_fail_closed(token):
    _fail_closed.reset(token)


def tenant_queries_fail_closed() -> bool:
    """When True, TenantManager returns no rows unless an org is in context."""
    return bool(_fail_closed.get())


@contextmanager
def organization_context(organization):
    """Temporarily run a block scoped to ``organization`` (e.g. in tasks/tests)."""
    token = set_current_organization(organization)
    try:
        yield organization
    finally:
        clear_current_organization(token)
