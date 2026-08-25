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

RUN chmod +x start.sh

# collectstatic at image build (no live DB). Use non-localhost dummies so
# production.py boot checks pass without connecting.
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=build-collectstatic-only-not-a-real-secret \
    DATABASE_URL=postgres://build:build@db.invalid/build \
    CELERY_BROKER_URL=redis://redis.invalid:6379/0 \
    REDIS_URL=redis://redis.invalid:6379/0 \
    ALLOW_DUMMY_BILLING_IN_PRODUCTION=True \
    BILLING_PROVIDER=dummy \
    REQUIRE_SENTRY=False \
    EMAIL_HOST=smtp.example.com \
    CORS_ALLOWED_ORIGINS=https://example.com \
    FRONTEND_URL=https://example.com \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["./start.sh"]
