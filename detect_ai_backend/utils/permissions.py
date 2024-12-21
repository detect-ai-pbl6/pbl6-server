from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, permissions, status

from detect_ai_backend.api_keys.models import APIKey


class LimitExceededException(exceptions.APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("API key usage limit exceeded")
    default_code = "api_key_limit_exceedd"


class APIKeyNotDefaultException(exceptions.APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = _("This API key is not enable for use.")
    default_code = "api_key_not_default"


class HasAPIKey(permissions.BasePermission):
    def has_permission(self, request, view):
        api_key = request.headers.get("x-api-key", "")
        is_authenticated = False
        api_key_instance = None
        if request.user and request.user.is_authenticated and api_key:
            try:
                api_key_instance = APIKey.objects.get(
                    api_key=api_key, user=request.user
                )
                if api_key_instance.total_usage >= api_key_instance.maximum_usage:
                    raise LimitExceededException
                if not api_key_instance.is_active:
                    raise APIKeyNotDefaultException
                is_authenticated = True
            except APIKey.DoesNotExist:
                pass
        request.api_key = api_key_instance
        return is_authenticated


class IsAuthenticatedButNotAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not (request.user.is_staff or request.user.is_superuser)
        )
