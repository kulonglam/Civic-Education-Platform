from .models import ActivityLog


def log_activity(user, activity_type, metadata=None, organization=None):
    from apps.tenants.context import get_current_organization

    if organization is None:
        organization = get_current_organization()
    ActivityLog.objects.create(
        user=user if user and user.is_authenticated else None,
        organization=organization,
        activity_type=activity_type,
        metadata=metadata or {},
    )
