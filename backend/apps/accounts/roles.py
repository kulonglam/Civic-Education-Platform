"""Platform role names and permission groups.

Two authorization planes (do not mix them):

* **Platform** (``User.role``): ``admin`` and ``super_admin`` operate the
  product — organizations, subscriptions, platform users, security events,
  and system-wide analytics. ``super_admin`` additionally manages tenant
  lifecycle, cross-org usage, and SLO.
* **Tenant** (``Membership.role``): ``owner`` and ``admin`` operate **one**
  organization — members, courses, lessons, quizzes, discussions, events,
  and that org's reports. They have no access to another organization's
  data; ``X-Tenant-Slug`` for a foreign org is ignored.

Guest is unauthenticated (no Role row). Citizen/Learner is ``citizen``.
Content Creator is stored as ``editor`` for compatibility. Administrator is
``admin``. Super Admin is ``super_admin``.
"""

from __future__ import annotations

CITIZEN = 'citizen'
EDITOR = 'editor'
MODERATOR = 'moderator'
ADMIN = 'admin'
SUPER_ADMIN = 'super_admin'

ALL_PLATFORM_ROLES = (CITIZEN, EDITOR, MODERATOR, ADMIN, SUPER_ADMIN)

# Operational administrators (full system control) plus super admins
PLATFORM_ADMIN_ROLES = frozenset({ADMIN, SUPER_ADMIN})
CONTENT_ROLES = frozenset({EDITOR, ADMIN, SUPER_ADMIN})
MODERATION_ROLES = frozenset({MODERATOR, ADMIN, SUPER_ADMIN})
LEARNER_ROLES = frozenset(ALL_PLATFORM_ROLES)
CONFIG_ROLES = frozenset({SUPER_ADMIN})

ASSIGNABLE_BY_ADMIN = frozenset({CITIZEN, EDITOR, MODERATOR})
ASSIGNABLE_BY_SUPER_ADMIN = ASSIGNABLE_BY_ADMIN | {ADMIN, SUPER_ADMIN}


def role_name(user) -> str | None:
    return getattr(getattr(user, 'role', None), 'name', None)


def is_platform_admin(user) -> bool:
    return role_name(user) in PLATFORM_ADMIN_ROLES


def is_super_admin(user) -> bool:
    return role_name(user) == SUPER_ADMIN


def assignable_roles_for(user) -> frozenset[str]:
    if is_super_admin(user):
        return ASSIGNABLE_BY_SUPER_ADMIN
    if role_name(user) == ADMIN:
        return ASSIGNABLE_BY_ADMIN
    return frozenset()
