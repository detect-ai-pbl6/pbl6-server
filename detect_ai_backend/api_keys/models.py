import secrets

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from detect_ai_backend.users.models import User

# Create your models here.


def api_key_generator():
    return f"ak_{secrets.token_urlsafe(28)}"


class APIKeyType(models.TextChoices):
    FREE_TIER = "free_tier"
    ENTERPRISE_TIER = "enterprise_tier"
    CUSTOM_TIER = "custom_tier"


class APIKey(models.Model):
    api_key = models.CharField(default=api_key_generator, max_length=42, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(blank=True, null=True, default=None)
    api_key_type = models.CharField(
        choices=APIKeyType.choices, default=APIKeyType.FREE_TIER, max_length=15
    )
    maximum_usage = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    total_usage = models.BigIntegerField(default=0, validators=[MinValueValidator(0)])
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Set maximum usage based on API key type if not explicitly set
        if not self.maximum_usage:
            if self.api_key_type == APIKeyType.FREE_TIER:
                self.maximum_usage = 100
            elif self.api_key_type == APIKeyType.ENTERPRISE_TIER:
                self.maximum_usage = 10000
            elif self.api_key_type == APIKeyType.CUSTOM_TIER:
                self.maximum_usage = 10000
        if self.is_default:
            api_keys = APIKey.objects.filter(user=self.user)
            for key in api_keys:
                key.is_default = False
                key.save()

        if self.total_usage > self.maximum_usage:
            self.total_usage = self.maximum_usage

        super().save(*args, **kwargs)


class APIKeyLogStatus(models.TextChoices):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"


class APIKeyLog(models.Model):
    api_key = models.ForeignKey(APIKey, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        choices=APIKeyLogStatus.choices, default=APIKeyLogStatus.PENDING, max_length=15
    )
