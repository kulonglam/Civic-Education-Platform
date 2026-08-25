#!/bin/sh
set -e

# Boot entrypoint for Render Docker (no Shell required).
# Keep this free of nested quoting so the dashboard Docker Command can be: ./start.sh
python manage.py migrate --noinput
python manage.py seed_data
exec daphne -b 0.0.0.0 -p "${PORT:-8000}" config.asgi:application
