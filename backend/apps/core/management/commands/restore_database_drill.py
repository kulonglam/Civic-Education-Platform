"""Disaster-recovery restore drill.

Creates a logical backup of the current database, restores it into a temporary
PostgreSQL database, verifies core tables exist, then drops the temp DB.

Use in CI or staging (never point --target-db at production).
"""

from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


CORE_TABLES = (
    'users',
    'organizations',
    'articles',
    'activity_logs',
)


class Command(BaseCommand):
    help = 'Backup → restore into a temp DB → verify tables (DR drill).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--target-db',
            default=os.environ.get('RESTORE_DRILL_DB', 'civic_education_restore_drill'),
            help='Temporary database name used for the restore (destroyed after).',
        )
        parser.add_argument(
            '--keep-backup',
            action='store_true',
            help='Keep the intermediate .sql.gz backup file.',
        )
        parser.add_argument(
            '--skip-drop',
            action='store_true',
            help='Do not drop the target DB after verification (debug only).',
        )

    def handle(self, *args, **options):
        database = settings.DATABASES['default']
        engine = database.get('ENGINE', '')
        if 'postgresql' not in engine and 'postgis' not in engine:
            raise CommandError('restore_database_drill only supports PostgreSQL.')

        for tool in ('pg_dump', 'psql', 'createdb', 'dropdb'):
            if shutil.which(tool) is None:
                raise CommandError(f'{tool} not found on PATH. Install PostgreSQL client tools.')

        source_name = database.get('NAME')
        if not source_name:
            raise CommandError('Database NAME is not configured.')

        target_db = options['target_db']
        if target_db == source_name:
            raise CommandError('Refusing to restore into the live source database name.')

        env = os.environ.copy()
        self._apply_password(env, database)

        with tempfile.TemporaryDirectory(prefix='cep-dr-') as tmp:
            dump_path = Path(tmp) / 'drill_backup.sql.gz'
            self.stdout.write(f'Dumping {source_name} → {dump_path}...')
            self._dump(database, env, dump_path)

            keep_path = None
            if options['keep_backup']:
                keep_dir = Path(settings.BASE_DIR) / 'backups'
                keep_dir.mkdir(parents=True, exist_ok=True)
                keep_path = keep_dir / 'last_restore_drill.sql.gz'
                shutil.copy2(dump_path, keep_path)
                self.stdout.write(f'Kept backup at {keep_path}')

            self.stdout.write(f'Recreating target database {target_db}...')
            self._drop_db(database, env, target_db, ignore_missing=True)
            self._create_db(database, env, target_db)

            self.stdout.write(f'Restoring into {target_db}...')
            self._restore(database, env, target_db, dump_path)

            self.stdout.write('Verifying core tables...')
            missing = self._missing_tables(database, env, target_db)
            if missing:
                raise CommandError(f'Restore drill failed; missing tables: {", ".join(missing)}')

            if not options['skip_drop']:
                self.stdout.write(f'Dropping drill database {target_db}...')
                self._drop_db(database, env, target_db, ignore_missing=False)

        self.stdout.write(self.style.SUCCESS('Disaster-recovery restore drill passed.'))

    def _dump(self, database, env, outfile: Path):
        cmd = ['pg_dump', '--no-owner', '--no-acl', '--format=plain']
        self._apply_conn(cmd, database)
        cmd.append(database['NAME'])
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'pg_dump failed.')
        with gzip.open(outfile, 'wb') as gz:
            gz.write(proc.stdout)

    def _restore(self, database, env, target_db: str, dump_path: Path):
        cmd = ['psql', '--set', 'ON_ERROR_STOP=1', '-d', target_db, '-v', 'ON_ERROR_STOP=1']
        self._apply_conn(cmd, database)
        with gzip.open(dump_path, 'rb') as gz:
            sql = gz.read()
        proc = subprocess.run(cmd, env=env, input=sql, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'psql restore failed.')

    def _missing_tables(self, database, env, target_db: str) -> list[str]:
        missing = []
        for table in CORE_TABLES:
            cmd = [
                'psql',
                '-d',
                target_db,
                '-tAc',
                f"SELECT to_regclass('public.{table}')",
            ]
            self._apply_conn(cmd, database)
            proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if proc.returncode != 0:
                raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'table check failed.')
            value = proc.stdout.decode('utf-8').strip()
            if value in ('', 'null', 'NULL'):
                missing.append(table)
        return missing

    def _create_db(self, database, env, name: str):
        cmd = ['createdb']
        self._apply_conn(cmd, database)
        cmd.append(name)
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'createdb failed.')

    def _drop_db(self, database, env, name: str, *, ignore_missing: bool):
        cmd = ['dropdb']
        if ignore_missing:
            cmd.append('--if-exists')
        self._apply_conn(cmd, database)
        cmd.append(name)
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0 and not ignore_missing:
            raise CommandError(proc.stderr.decode('utf-8', errors='replace') or 'dropdb failed.')

    @staticmethod
    def _apply_conn(cmd, database):
        if database.get('HOST'):
            cmd.extend(['-h', database['HOST']])
        if database.get('PORT'):
            cmd.extend(['-p', str(database['PORT'])])
        if database.get('USER'):
            cmd.extend(['-U', database['USER']])

    @staticmethod
    def _apply_password(env, database):
        if database.get('PASSWORD'):
            env['PGPASSWORD'] = database['PASSWORD']
