"""
Production settings
"""

from google.auth import default
from google.auth.transport import requests
from google.cloud import storage

from .common import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = os.getenv("ENV", default="dev") == "dev"  # noqa
DEBUG = True
# SECRET_KEY = os.getenv(  # noqa
#     "SECRET_KEY", "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"
# )
SECRET_KEY = "U.gM-V)D5Z{CA303?eJ%Kr-}48CfM#p}0GzcE[BD*pa;;PPwrq/U7J!n{e9H"
ALLOWED_HOSTS = [os.getenv("ALLOWED_HOSTS", "*")]  # noqa

HOST = os.getenv("HOST", "http://localhost:8000/")  # noqa

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.getenv("DB_NAME", "detect_ai_backend"),  # noqa
        "USER": os.getenv("DB_USERNAME", "postgres"),  # noqa
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),  # noqa
        "HOST": os.getenv("DB_HOST", "localhost"),  # noqa
        "PORT": "5432",
    }
}

# CORS config
# CORS_ALLOWED_ORIGINS = os.getenv(  # noqa
#     "CORS_ALLOWED_ORIGINS", "http://localhost:3000, http://localhost:8000, http://localhost:7000"
# ).split(",")
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:7000",
]

GCP_CREDENTIALS, _ = default()
GCP_CREDENTIALS.refresh(requests.Request())
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "")  # noqa
GCP_STORAGE_CLIENT = storage.Client(credentials=GCP_CREDENTIALS)
GCP_FILES_BUCKET = GCP_STORAGE_CLIENT.get_bucket(GCP_BUCKET_NAME)
GCP_STORAGE_URL = f"https://storage.googleapis.com/{GCP_BUCKET_NAME}"  # noqa
