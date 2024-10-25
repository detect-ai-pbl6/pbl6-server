
---

# Django template

## Prerequisites
- [Python](https://www.python.org/) v3.10
- [PostgreSQL](https://www.postgresql.org/)

## Setup

### Setup environment

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```
2. Update database information in `detect_ai_backend/settings/local.py`
3. Migrate database
   ```
   python manage.py migrate
   ```

### Launch
   ```
   python manage.py runserver 0.0.0.0:8000
   ```
