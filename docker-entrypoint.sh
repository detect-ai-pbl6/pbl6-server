#!/bin/bash

echo "Apply database migrations"
python3 manage.py migrate

echo "Starting collectstatic"
python3 manage.py collectstatic

echo "Starting server"
daphne -b 0.0.0.0 -p 80 detect_ai_backend.asgi:application
