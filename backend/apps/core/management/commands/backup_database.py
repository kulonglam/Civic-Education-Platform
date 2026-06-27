"""Create a PostgreSQL logical backup using pg_dump."""

import gzip
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Dump the PostgreSQL database to a compressed SQL file (production backups).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            default=os.environ.get('BACKUP_DIR', ''),
            help='Directory for backup files (default: BACKUP_DIR env or ./backups)',
        )
        parser.add_argument(
            '--retain',
            type=int,
            default=int(os.environ.get('BACKUP_RETAIN_DAYS', '14')),
            help='Delete backups older than this many days (0 = keep all)',
        )

    def handle(self, *args, **options):
        database = settings.DATABASES['default']
        engine = database.get('ENGINE', '')
        if 'postgresql' not in engine and 'postgis' not in engine:
            raise CommandError('backup_database only supports PostgreSQL.')

        pg_dump = shutil.which('pg_dump')
        if pg_dump is None:
            raise CommandError('pg_dump not found on PATH. Install PostgreSQL client tools.')

        output_dir = Path(options['output_dir'] or (settings.BASE_DIR / 'backups'))
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        outfile = output_dir / f'civic_education_{timestamp}.sql.gz'

        env = os.environ.copy()
        cmd = [pg_dump, '--no-owner', '--no-acl', '--format=plain']

        if database.get('NAME'):
            self._apply_conn(cmd, env, database)
        else:
            raise CommandError('Database NAME is not configured.')

        self.stdout.write(f'Writing backup to {outfile}...')
        with gzip.open(outfile, 'wb') as gz:
            proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if proc.returncode != 0:
                raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'pg_dump failed.')
            gz.write(proc.stdout)

        size_mb = outfile.stat().st_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(f'Backup complete ({size_mb:.2f} MB): {outfile}'))

        retain = options['retain']
        if retain > 0:
            self._prune_old_backups(output_dir, retain)

    @staticmethod
    def _apply_conn(cmd, env, database):
        if database.get('HOST'):
            cmd.extend(['-h', database['HOST']])
        if database.get('PORT'):
            cmd.extend(['-p', str(database['PORT'])])
        if database.get('USER'):
            cmd.extend(['-U', database['USER']])
        if database.get('PASSWORD'):
            env['PGPASSWORD'] = database['PASSWORD']
        cmd.append(database['NAME'])

    def _prune_old_backups(self, output_dir: Path, retain_days: int):
        cutoff = datetime.utcnow().timestamp() - (retain_days * 86400)
        removed = 0
        for path in output_dir.glob('civic_education_*.sql.gz'):
            if path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
        if removed:
            self.stdout.write(f'Pruned {removed} backup(s) older than {retain_days} days.')
