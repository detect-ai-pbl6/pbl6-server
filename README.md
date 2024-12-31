
---

# Django template

## Prerequisites
- [Python](https://www.python.org/) v3.10
- [PostgreSQL](https://www.postgresql.org/)

## Setup

### Setup environment

1. Install dependencies for development
   ```
   pip install -r requirements-dev.txt
   ```
2. Update database information in `detect_ai_backend/settings/local.py`
3. Migrate database
   ```
   python manage.py migrate
   ```

### Launch
1. First terminal
   ```
   python manage.py runserver
   ```
2. Second terminal
   ```
   celery -A detect_ai_backend worker -l INFO --concurrency 2 -P solo -E -n worker1
   ```
