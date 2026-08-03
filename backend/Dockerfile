FROM python:3.13-slim

# Keep Python output unbuffered so logs surface immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production

WORKDIR /app

# Install system deps required by psycopg2-binary and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static files at build time (requires dummy env values)
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-dummy \
    DATABASE_URL=postgres://x:x@localhost/x \
    python manage.py collectstatic --noinput || true

EXPOSE 8000

# Free-tier hosts often lack Shell — migrate + seed on boot.
# Override with a Celery worker command in docker-compose / Render Background Worker.
CMD sh -c "python manage.py migrate --noinput && python manage.py seed_data && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120"
