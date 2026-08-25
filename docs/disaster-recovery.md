# Disaster recovery

Backup and restore procedures for the Civic Education RSS (PostgreSQL).

## Automated backup

```bash
cd backend
python manage.py backup_database --output-dir /var/data/backups --retain 14
```

Schedule weekly (or daily) via cron / Render cron. Env vars:

| Variable | Purpose |
|----------|---------|
| `BACKUP_DIR` | Output directory |
| `BACKUP_RETAIN_DAYS` | Prune age (default 14) |
| `AUDIT_WORM_PATH` | JSONL append replica of the audit hash chain (optional) |

On Render, the backup cron uses a **persistent disk** at `/var/data/backups`. When storage credentials are configured, `backup_database` also copies the dump to object storage under `backups/`.

The JSONL worm file is **application-level** append-only. True WORM (S3 Object Lock, Azure immutable blob, or a WORM appliance) is a hosting choice.

## Restore drill (required before audits)

Proves backups are restorable without touching the live DB name:

```bash
cd backend
python manage.py restore_database_drill
```

What it does:

1. `pg_dump` the current database  
2. `createdb` a temporary DB (`civic_education_restore_drill` by default)  
3. Restore the dump into that DB  
4. Verify core tables exist (`accounts_user`, `organizations`, `articles`, `activity_logs`)  
5. Drop the temporary DB  

Flags:

- `--target-db NAME` — alternate temp database  
- `--keep-backup` — copy drill dump to `backups/last_restore_drill.sql.gz`  
- `--skip-drop` — leave the temp DB for inspection  

**Never** set `--target-db` to the production database name (the command refuses that).

## Manual restore (true incident)

1. Stop writers (web/worker) or put the app in maintenance.  
2. Provision / empty the target database.  
3. Restore:

```bash
gunzip -c civic_education_YYYYMMDDT….sql.gz | psql -h … -U … -d civic_education
```

4. Run `python manage.py migrate` if schema moved ahead of the dump.  
5. Start services; verify `GET /api/ready/` and a login smoke test.

## CI

The GitHub Actions `disaster-recovery` job runs `restore_database_drill` against the CI Postgres service after migrate + seed.

## RPO / RTO targets (ops commitment)

| Metric | Target | Notes |
|--------|--------|-------|
| RPO | ≤ 24h | Daily backups; tighten with managed PITR if required |
| RTO | ≤ 4h | Restore drill + DNS/cutover runbook |

Document actual hosting provider snapshot/PITR settings alongside this file for enterprise buyers.
