# Monorepo entrypoint for Render Docker deploys (repo root context).
# Prefer the render.yaml Blueprint (runtime: python) — it avoids Docker and
# provisions API, worker, Redis, Postgres, cron jobs, and static frontend together.

FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY backend/ .

# collectstatic needs dummy env at build time; real env is injected at runtime.
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-dummy \
    DATABASE_URL=postgres://x:x@localhost/x \
    CELERY_BROKER_URL=redis://localhost:6379/0 \
    python manage.py collectstatic --noinput || true

EXPOSE 8000

# Free-tier hosts often lack Shell — migrate + seed on boot.
CMD sh -c "python manage.py migrate --noinput && python manage.py seed_data && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"
