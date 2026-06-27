# Scaling & Operations

This document covers the asynchronous task architecture and how to load-test the
platform against the SRS scale targets (50,000 registered users, 10,000
concurrent users).

## Background tasks (Celery + Redis)

Work that is slow or unbounded by user count runs off the request path via
Celery so API responses stay fast:

| Task | Module | Trigger |
| --- | --- | --- |
| `broadcast_notification_task` | `apps/notifications/tasks.py` | Publishing an article (fan-out to all active users, batched) |
| `send_email_task` | `apps/core/tasks.py` | Registration verification + password reset emails (with retry + logging) |
| `generate_certificate_pdf_task` | `apps/quizzes/tasks.py` | Passing a quiz (renders the PDF and uploads it to storage) |

### Eager fallback (dev / test)

The broker is **optional** in development. `CELERY_TASK_ALWAYS_EAGER` defaults
to the value of `DEBUG`, so tasks run inline (synchronously) when `DEBUG=True`
and no Redis is required. Tests force eager mode in `config/settings/test.py`.

### Running asynchronously (production-like)

1. Start Redis (broker):

   ```bash
   docker run -p 6379:6379 redis:7
   ```

2. In `backend/.env` set:

   ```env
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_TASK_ALWAYS_EAGER=False
   ```

3. Start a worker (a `start-worker.cmd` helper is provided for Windows):

   ```bash
   celery -A config worker --loglevel=info
   # Windows: use --pool=solo
   ```

In production (`config.settings.production`, `DEBUG=False`) async mode is the
default; just point `CELERY_BROKER_URL` at your managed Redis and run one or
more worker processes (e.g. a separate Render worker service).

## Load testing (Locust)

A Locust scenario lives at `backend/loadtest/locustfile.py`. It registers and
logs in a unique user, then loops through realistic read-heavy traffic
(articles, quizzes, forum, notifications, profile) with a small write share.

### Quick run (local, web UI)

```bash
cd backend
locust -f loadtest/locustfile.py --host http://localhost:8000
# open http://localhost:8089
```

### Headless ramp toward the SRS concurrency target

```bash
cd backend
locust -f loadtest/locustfile.py --host http://localhost:8000 \
    --users 10000 --spawn-rate 200 --run-time 10m --headless
```

### CI load-test gate

GitHub Actions runs a short headless Locust smoke test on every push/PR (`loadtest` job in `.github/workflows/ci.yml`):

```bash
cd backend
python manage.py migrate && python manage.py seed_data
python manage.py runserver 127.0.0.1:8000 &
python loadtest/ci_gate.py --host http://127.0.0.1:8000 --users 8 --spawn-rate 2 --run-time 20s
```

The CI scenario lives in `loadtest/ci_locustfile.py` (seeded admin login + read-heavy paths). The full registration ramp remains in `loadtest/locustfile.py`.

### Getting meaningful numbers

- Test a **production-like** stack: `DEBUG=False`, gunicorn (multiple workers),
  PostgreSQL, Redis, and a running Celery worker. The Django dev server is
  single-threaded and will not represent real capacity.
- Driving 10,000 concurrent users from one machine is usually not possible.
  Use Locust **distributed mode**: one `--master` and several `--worker`
  processes, typically spread across multiple load-generator hosts.

  ```bash
  # master
  locust -f loadtest/locustfile.py --master --host http://your-host
  # each worker (repeat / scale out)
  locust -f loadtest/locustfile.py --worker --master-host <master-ip>
  ```

- Seed representative content first (`python manage.py seed_data`) so reads hit
  real rows.

### SRS targets to validate

| Metric | Target |
| --- | --- |
| Registered users | 50,000 |
| Concurrent users | 10,000 |
| API response (typical) | fast under nominal load — watch p95/p99 latency |

Watch the Locust percentile table (p50/p95/p99) and failure rate as you ramp.
Rising p99 or failures is the signal to scale web workers, the database, or add
caching / read replicas.
