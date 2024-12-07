"""
Production settings
"""

from .common import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

DEBUG = False

SECRET_KEY = (
    "django-insecure-*$0b8ibx7uzk45cm+fxw7*jj(yzi2ye!l4+!dnyxa-u-nbuz=q"  # nosec
)

ALLOWED_HOSTS = ["*"]

HOST = "http://localhost:8000/"

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "../db.sqlite3"),  # noqa
    }
}

# CORS config
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    "https://localhost:5173",
    "https://127.0.0.1:5173",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]

CSRF_TRUSTED_ORIGINS = ["http://localhost:5173", "https://127.0.0.1:5173"]

GCP_CREDENTIALS = {}
GCP_BUCKET_NAME = {}  # noqa
GCP_STORAGE_CLIENT = {}
GCP_FILES_BUCKET = "abc"
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
    # "github": {
    #     "SCOPE": [
    #         "user",
    #         "repo",
    #         "read:org",
    #     ],
    #     "APP": {
    #         "client_id": os.getenv("GITHUB_CLIENT_ID", ""),  # noqa
    #         "secret": os.getenv("GITHUB_SECRET", ""),  # noqa
    #     },
    # },
}

SESSION_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}
SUPERUSER_EMAIL = "admin@gmail.com"  # nosec
SUPERUSER_PASSWORD = "123123"  # nosec
ADMIN_ORIGIN = "http://localhost:3000"