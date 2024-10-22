#!/bin/bash

echo "Apply database migrations"
python3 manage.py migrate

echo "Starting collectstatic"
python3 manage.py collectstatic

echo "Starting server"
gunicorn --bind 0.0.0.0:80 --access-logfile - detect_ai_backend.wsgi
