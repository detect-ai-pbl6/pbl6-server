"""
Production settings
"""

from google.auth import default
from google.auth.transport import requests
from google.cloud import storage

from .common import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = False
# SECRET_KEY = os.getenv(  # noqa
#     "SECRET_KEY", "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"
# )
SECRET_KEY = os.getenv("SECRET_KEY", "")  # noqa  # nosec
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

PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # noqa
PUBLIC_KEY = os.getenv("PUBLIC_KEY")  # noqa

SIMPLE_JWT.update(  # noqa
    {
        "SIGNING_KEY": PRIVATE_KEY,
        "VERIFYING_KEY": PUBLIC_KEY,
    }
)
# CORS config
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")  # noqa
CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",")  # noqa


GCP_CREDENTIALS, _ = default()
GCP_CREDENTIALS.refresh(requests.Request())
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME", "")  # noqa
GCP_STORAGE_CLIENT = storage.Client(credentials=GCP_CREDENTIALS)
GCP_FILES_BUCKET = GCP_STORAGE_CLIENT.get_bucket(GCP_BUCKET_NAME)
GCP_STORAGE_URL = f"https://storage.googleapis.com/{GCP_BUCKET_NAME}"  # noqa


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),  # noqa
            "secret": os.getenv("GOOGLE_SECRET", ""),  # noqa
            "key": "",
        },
    },
    "github": {
        "SCOPE": [
            "user",
            "repo",
            "read:org",
        ],
        "APP": {
            "client_id": os.getenv("GITHUB_CLIENT_ID", ""),  # noqa
            "secret": os.getenv("GITHUB_SECRET", ""),  # noqa
        },
    },
}

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"


SUPERUSER_EMAIL = os.getenv("SUPERUSER_EMAIL", "")  # noqa
SUPERUSER_PASSWORD = os.getenv("SUPERUSER_PASSWORD", "")  # noqa
ADMIN_ORIGIN = os.getenv("ADMIN_ORIGIN", "")  # noqa

MESSAGE_BROKER_USERNAME = os.getenv("MESSAGE_BROKER_USERNAME", "")  # noqa
MESSAGE_BROKER_PASSWORD = os.getenv("MESSAGE_BROKER_PASSWORD", "")  # noqa
MESSAGE_BROKER_HOST = os.getenv("MESSAGE_BROKER_HOST", "")  # noqa
MESSAGE_BROKER_VHOST = os.getenv("MESSAGE_BROKER_VHOST", "")  # noqa
CELERY_APP_NAME = "detect_ai_backend"
CELERY_BROKER_URL = f"amqp://{MESSAGE_BROKER_USERNAME}:{MESSAGE_BROKER_PASSWORD}@{MESSAGE_BROKER_HOST}/{MESSAGE_BROKER_VHOST}"  # noqa
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_rabbitmq.core.RabbitmqChannelLayer",
        "CONFIG": {
            "host": f"amqp://{MESSAGE_BROKER_USERNAME}:{MESSAGE_BROKER_PASSWORD}@{MESSAGE_BROKER_HOST}/{MESSAGE_BROKER_VHOST}",  # noqa
        },
    }
}
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
AI_SERVER_NAME = os.getenv("AI_SERVER_NAME", "")  # noqa
