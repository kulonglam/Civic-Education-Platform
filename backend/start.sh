#!/bin/sh
set -e

# Boot entrypoint for Render Docker (no Shell required).
# Keep this free of nested quoting so the dashboard Docker Command can be: ./start.sh
python manage.py migrate --noinput
python manage.py seed_data
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 120
