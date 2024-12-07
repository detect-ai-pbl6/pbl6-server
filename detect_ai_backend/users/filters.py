from django_filters import rest_framework as filters

from detect_ai_backend.users.models import User


class UserFilter(filters.FilterSet):
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")

    class Meta:
        model = User
        fields = [
            "email",
        ]
