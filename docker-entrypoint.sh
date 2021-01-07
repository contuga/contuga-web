#!/bin/sh

echo "Collecting static files"
python3 manage.py collectstatic --noinput

echo "Applying database migrations"
python3 manage.py migrate

echo "Starting server"
# uwsgi --ini uwsgi.ini
gunicorn contuga.wsgi:application -w 2 -b :8000
