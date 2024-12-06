from rest_framework.permissions import BasePermission

from detect_ai_backend.api_keys.models import APIKey


class HasAPIKey(BasePermission):

    def has_permission(self, request, view):
        api_key = request.headers.get("x-api-key", "")
        is_authenticated = False
        if request.user and request.user.is_authenticated and api_key:
            try:
                APIKey.objects.get(api_key=api_key, user=request.user)
                is_authenticated = True
            except APIKey.DoesNotExist:
                pass
        request.api_key = api_key
        return is_authenticated
