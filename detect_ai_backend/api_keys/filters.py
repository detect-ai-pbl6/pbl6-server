from django_filters import rest_framework as filters

from detect_ai_backend.api_keys.models import APIKey


class APIKeysFilter(filters.FilterSet):
    user = filters.CharFilter(field_name="user__email", lookup_expr="icontains")

    class Meta:
        model = APIKey
        fields = ["user"]
