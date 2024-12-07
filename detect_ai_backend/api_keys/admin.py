from django.contrib import admin

from detect_ai_backend.api_keys.models import APIKey, APIKeyLog

# Register your models here.
admin.site.register(APIKey)
admin.site.register(APIKeyLog)
