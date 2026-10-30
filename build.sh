#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Create a superuser automatically (if it doesn't exist)
DJANGO_SUPERUSER_PASSWORD=OmniGo2026! python manage.py createsuperuser --noinput --username admin --email admin@omnigo.com || true