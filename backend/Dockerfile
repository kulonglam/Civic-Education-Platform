FROM python:3.13-slim

# Keep Python output unbuffered so logs surface immediately
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

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

# Default: run with Daphne (ASGI / Channels) for WebSocket support.
# Override CMD in docker-compose for the Celery worker.
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
