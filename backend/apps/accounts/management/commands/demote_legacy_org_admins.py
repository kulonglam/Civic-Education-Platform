from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apps.accounts.models import Role
from apps.tenants.models import Membership

User = get_user_model()


class Command(BaseCommand):
    help = (
        'Demote platform admin role to editor for org owners who are not Django superusers. '
        'Keeps the seeded platform superuser unchanged.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print affected users without saving changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        try:
            admin_role = Role.objects.get(name='admin')
            editor_role = Role.objects.get(name='editor')
        except Role.DoesNotExist:
            self.stderr.write('Run seed_data first to create roles.')
            return

        candidates = (
            User.objects.filter(role=admin_role, memberships__role=Membership.OWNER)
            .exclude(is_superuser=True)
            .distinct()
        )

        count = 0
        for user in candidates:
            count += 1
            message = f'{user.email} → editor'
            if dry_run:
                self.stdout.write(f'[dry-run] Would demote {message}')
            else:
                user.role = editor_role
                user.save(update_fields=['role'])
                self.stdout.write(self.style.SUCCESS(f'Demoted {message}'))

        if count == 0:
            self.stdout.write('No legacy org-owner platform admins found.')
        elif dry_run:
            self.stdout.write(f'Would demote {count} user(s). Re-run without --dry-run to apply.')
