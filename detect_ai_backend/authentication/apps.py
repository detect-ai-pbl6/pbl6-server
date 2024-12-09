from django.apps import AppConfig


class RefreshTokensConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "detect_ai_backend.authentication"

    def ready(self):
        import detect_ai_backend.authentication.socials_signals  # noqa

        return super().ready()
