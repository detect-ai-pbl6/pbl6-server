from django_filters import rest_framework as filters

from detect_ai_backend.history.models import History


class HistoryFilter(filters.FilterSet):
    user = filters.CharFilter(field_name="user__email", lookup_expr="icontains")

    class Meta:
        model = History
        fields = ["user"]
