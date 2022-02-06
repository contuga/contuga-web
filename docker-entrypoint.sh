#!/bin/sh

echo "Collecting static files"
python3 manage.py collectstatic --noinput

echo "Applying database migrations"
python3 manage.py migrate

echo "Compiling translations"
python3 ./manage.py compilemessages

echo "Starting server"
gunicorn contuga.wsgi:application -w 2 -b :8000 --access-logfile "-"
# uwsgi --http :8000 --module contuga.wsgi
