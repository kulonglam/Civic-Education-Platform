from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.core.tasks import send_email_task

from .models import Membership, Organization, OrganizationInvite


def generate_unique_slug(name: str) -> str:
    base = slugify(name) or 'org'
    slug = base
    i = 1
    while Organization.objects.filter(slug=slug).exists():
        i += 1
        slug = f'{base}-{i}'
    return slug


@transaction.atomic
def create_organization_with_owner(*, name: str, owner, slug: str | None = None) -> Organization:
    """Create an organization and make ``owner`` its owner member."""
    organization = Organization.objects.create(
        name=name,
        slug=slug or generate_unique_slug(name),
    )
    Membership.objects.create(
        organization=organization,
        user=owner,
        role=Membership.OWNER,
    )
    return organization


def get_user_organization(user):
    """Return the user's primary organization (first membership), or None."""
    membership = (
        Membership.objects.filter(user=user)
        .select_related('organization')
        .order_by('created_at')
        .first()
    )
    return membership.organization if membership else None


def join_public_organization(user) -> Organization | None:
    """Add a citizen to the platform's public learning workspace."""
    slug = getattr(settings, 'PUBLIC_ORGANIZATION_SLUG', 'platform-demo')
    organization = Organization.objects.filter(slug=slug, is_active=True).first()
    if organization is None:
        return None
    Membership.objects.get_or_create(
        organization=organization,
        user=user,
        defaults={'role': Membership.MEMBER},
    )
    return organization


INVITE_TTL_DAYS = 7


def get_valid_invite(token: str) -> OrganizationInvite | None:
    invite = (
        OrganizationInvite.objects.filter(token=token, accepted_at__isnull=True)
        .select_related('organization')
        .first()
    )
    if invite is None or invite.expires_at <= timezone.now():
        return None
    return invite


@transaction.atomic
def create_organization_invite(
    *,
    organization,
    email: str,
    role: str,
    invited_by,
    department=None,
) -> OrganizationInvite:
    """Create or refresh a pending invite and email the recipient."""
    email = email.lower().strip()
    OrganizationInvite.objects.filter(
        organization=organization,
        email=email,
        accepted_at__isnull=True,
    ).delete()

    invite = OrganizationInvite.objects.create(
        organization=organization,
        email=email,
        role=role,
        department=department,
        token=OrganizationInvite.generate_token(),
        invited_by=invited_by,
        expires_at=timezone.now() + timedelta(days=INVITE_TTL_DAYS),
    )
    invite_url = f'{settings.FRONTEND_URL}/invite/{invite.token}'
    send_email_task.delay(
        f'You are invited to join {organization.name}',
        (
            f'{invited_by.full_name if invited_by else "An administrator"} invited you to join '
            f'"{organization.name}" on the Civic Education Platform.\n\n'
            f'Accept your invitation: {invite_url}\n\n'
            f'This link expires in {INVITE_TTL_DAYS} days.'
        ),
        [email],
    )
    return invite


@transaction.atomic
def accept_organization_invite(*, invite: OrganizationInvite, user) -> Membership:
    """Accept a pending invite and return the new membership."""
    if not invite.is_pending:
        raise ValueError('Invite is no longer valid.')
    if user.email.lower() != invite.email.lower():
        raise ValueError('This invitation was sent to a different email address.')
    if Membership.objects.filter(organization=invite.organization, user=user).exists():
        invite.accepted_at = timezone.now()
        invite.save(update_fields=['accepted_at'])
        return Membership.objects.get(organization=invite.organization, user=user)

    membership = Membership.objects.create(
        organization=invite.organization,
        user=user,
        role=invite.role,
        department=invite.department,
    )
    invite.accepted_at = timezone.now()
    invite.save(update_fields=['accepted_at'])
    return membership


def resolve_department(organization, department_id=None, department_name: str | None = None):
    from django.utils.text import slugify

    from .models import Department

    if department_id:
        return Department.objects.filter(organization=organization, id=department_id).first()
    name = (department_name or '').strip()
    if not name:
        return None
    slug = slugify(name) or 'dept'
    dept, _ = Department.objects.get_or_create(
        organization=organization,
        slug=slug,
        defaults={'name': name},
    )
    return dept


@transaction.atomic
def bulk_provision_members(*, organization, rows, invited_by, dry_run=False, send_invites=True):
    """Provision members/invites from CSV-like rows. Returns a result summary."""
    from django.contrib.auth import get_user_model

    from apps.billing.services import check_quota

    User = get_user_model()
    results = {'created_memberships': 0, 'invites_sent': 0, 'errors': [], 'preview': []}

    for index, row in enumerate(rows, start=1):
        email = row['email'].lower().strip()
        role = row.get('role') or Membership.MEMBER
        if role == Membership.OWNER:
            results['errors'].append({'row': index, 'email': email, 'detail': 'Cannot assign owner via bulk import.'})
            continue
        department = resolve_department(
            organization,
            department_name=row.get('department') or '',
        )
        entry = {
            'row': index,
            'email': email,
            'role': role,
            'department': department.name if department else None,
            'action': None,
        }
        user = User.objects.filter(email=email).first()
        if user and Membership.objects.filter(organization=organization, user=user).exists():
            entry['action'] = 'already_member'
            results['preview'].append(entry)
            continue
        if user:
            entry['action'] = 'add_member'
            if not dry_run:
                try:
                    check_quota(organization, 'members')
                except Exception as exc:
                    results['errors'].append({'row': index, 'email': email, 'detail': str(exc)})
                    continue
                Membership.objects.create(
                    organization=organization,
                    user=user,
                    role=role,
                    department=department,
                )
                results['created_memberships'] += 1
            results['preview'].append(entry)
            continue

        entry['action'] = 'invite'
        if not dry_run and send_invites:
            try:
                check_quota(organization, 'members')
            except Exception as exc:
                results['errors'].append({'row': index, 'email': email, 'detail': str(exc)})
                continue
            create_organization_invite(
                organization=organization,
                email=email,
                role=role,
                invited_by=invited_by,
                department=department,
            )
            results['invites_sent'] += 1
        results['preview'].append(entry)

    return results