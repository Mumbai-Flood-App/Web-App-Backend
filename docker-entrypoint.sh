#!/bin/bash

# Wait for postgres
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn server.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
