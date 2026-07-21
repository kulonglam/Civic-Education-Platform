import hashlib
import json

from apps.tenants.context import get_current_organization

from .models import ActivityLog


def _client_meta(request=None) -> dict:
    if request is None:
        return {}
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    ip = forwarded.split(',')[0].strip() if forwarded else request.META.get('REMOTE_ADDR')
    ua = (request.META.get('HTTP_USER_AGENT') or '')[:512]
    return {'ip_address': ip or None, 'user_agent': ua}


def compute_integrity_hash(
    *,
    prev_hash: str,
    activity_type: str,
    user_id,
    organization_id,
    metadata: dict,
    timestamp_iso: str,
    ip_address,
) -> str:
    payload = '|'.join([
        prev_hash or '',
        activity_type,
        str(user_id or ''),
        str(organization_id or ''),
        json.dumps(metadata or {}, sort_keys=True, default=str),
        timestamp_iso,
        str(ip_address or ''),
    ])
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def log_activity(user, activity_type, metadata=None, organization=None, request=None):
    if organization is None:
        organization = get_current_organization()
    client = _client_meta(request)
    meta = metadata or {}

    prev = (
        ActivityLog.objects.filter(organization=organization)
        .order_by('-timestamp')
        .values_list('integrity_hash', flat=True)
        .first()
    ) or ''

    entry = ActivityLog.objects.create(
        user=user if user and getattr(user, 'is_authenticated', False) else None,
        organization=organization,
        activity_type=activity_type,
        metadata=meta,
        ip_address=client.get('ip_address'),
        user_agent=client.get('user_agent', ''),
        prev_hash=prev,
        integrity_hash='',
    )
    entry.integrity_hash = compute_integrity_hash(
        prev_hash=prev,
        activity_type=activity_type,
        user_id=entry.user_id,
        organization_id=entry.organization_id,
        metadata=meta,
        timestamp_iso=entry.timestamp.isoformat(),
        ip_address=entry.ip_address,
    )
    entry.save(update_fields=['integrity_hash'])
    return entry


def verify_audit_chain(organization=None, limit: int = 500) -> dict:
    """Verify hash-chain integrity for recent activity logs."""
    qs = ActivityLog.objects.all().order_by('timestamp')
    if organization is not None:
        qs = qs.filter(organization=organization)
    rows = list(qs[:limit])
    checked = 0
    broken_at = None
    for row in rows:
        if not row.integrity_hash:
            continue
        expected = compute_integrity_hash(
            prev_hash=row.prev_hash,
            activity_type=row.activity_type,
            user_id=row.user_id,
            organization_id=row.organization_id,
            metadata=row.metadata or {},
            timestamp_iso=row.timestamp.isoformat(),
            ip_address=row.ip_address,
        )
        checked += 1
        if expected != row.integrity_hash:
            broken_at = str(row.id)
            break
    return {
        'valid': broken_at is None,
        'checked': checked,
        'broken_at': broken_at,
        'organization_id': str(organization.id) if organization else None,
    }
