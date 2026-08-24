from apps.tenants.models import Membership
from apps.tenants.permissions import get_membership


def user_is_forum_expert(user) -> bool:
    """Editors, moderators, and org content leads can post expert replies."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    role = getattr(getattr(user, 'role', None), 'name', None)
    if role in ('editor', 'admin', 'super_admin', 'moderator'):
        return True
    membership = get_membership(user)
    return bool(
        membership
        and membership.role in (
            Membership.OWNER,
            Membership.ADMIN,
            Membership.CONTENT_MANAGER,
            Membership.MODERATOR,
        )
    )


def user_skips_forum_queue(user) -> bool:
    """Only platform moderators skip pre-moderation so citizen posts stay in the queue."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    role = getattr(getattr(user, 'role', None), 'name', None)
    return role in ('moderator', 'admin', 'super_admin')
