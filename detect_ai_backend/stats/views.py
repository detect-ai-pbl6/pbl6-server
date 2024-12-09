from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, response

from detect_ai_backend.api_keys.models import APIKey, APIKeyLog, APIKeyLogStatus
from detect_ai_backend.api_keys.serializers import DayGroupSerializer
from detect_ai_backend.stats.serializers import (
    StastsAPICallSerializer,
    StastsAPIKeysCreateSerializer,
    StastsSuccessActionSerializer,
    StatsCreatedUsersSerializer,
)
from detect_ai_backend.users.models import User


def calculate_monthly_stats(
    queryset,
    date_field,
    response_field: str,
    exclude_staff_filter: Q,
    status_filter=None,
):
    """
    Calculate monthly statistics for a given queryset.

    :param queryset: Django QuerySet to analyze
    :param date_field: Field to use for date filtering
    :param status_filter: Optional additional filter (e.g., for success status)
    :return: Dict with total count and growth percentage
    """
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

    # Apply additional status filter if provided
    if status_filter:
        current_month_queryset = queryset.filter(
            **{
                f"{date_field}__gte": current_month_start,
                f"{date_field}__lt": now,
                **status_filter,
            }
        )
        last_month_queryset = queryset.model.objects.filter(
            **{
                f"{date_field}__gte": last_month_start,
                f"{date_field}__lt": current_month_start,
                **status_filter,
            }
        )
    else:
        current_month_queryset = queryset.filter(
            **{f"{date_field}__gte": current_month_start, f"{date_field}__lt": now}
        )
        last_month_queryset = queryset.model.objects.filter(
            **{
                f"{date_field}__gte": last_month_start,
                f"{date_field}__lt": current_month_start,
            }
        )
    # Exclude staff and superusers
    current_month_count = current_month_queryset.exclude(exclude_staff_filter).count()
    last_month_count = last_month_queryset.exclude(exclude_staff_filter).count()

    # Calculate growth percentage
    growth_percentage = 0
    if last_month_count > 0:
        growth_percentage = (
            (current_month_count - last_month_count) / last_month_count
        ) * 100

    return {
        response_field: current_month_count,
        "growth_percentage": round(growth_percentage, 2),
    }


# Create your views here.
class StatsAPIKeyLogListView(generics.ListAPIView):
    queryset = APIKeyLog.objects.all()
    serializer_class = DayGroupSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

    ALL_STATUSES = [choice[0] for choice in APIKeyLogStatus.choices]

    @method_decorator(cache_page(10))
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Generate dates for the last 30 days
        today = now().date()
        thirty_days_ago = today - timedelta(days=30)
        date_range = [thirty_days_ago + timedelta(days=i) for i in range(31)]

        # Group by day and status, count the occurrences
        grouped_data = (
            queryset.annotate(day=TruncDate("timestamp"))
            .values("day", "status")
            .annotate(count=Count("id"))
        )

        # Create a dictionary to hold data for all days in the range
        response_data = {
            date: {"day": date, "statuses": {status: 0 for status in self.ALL_STATUSES}}
            for date in date_range
        }

        # Populate data for days with logs
        for item in grouped_data:
            day = item["day"]
            if day in response_data:
                response_data[day]["statuses"][item["status"]] = item["count"]

        # Transform statuses dictionary into a list
        final_response = [
            {
                "day": day_data["day"],
                "statuses": [
                    {"status": status, "count": count}
                    for status, count in day_data["statuses"].items()
                ],
            }
            for day_data in response_data.values()
        ]

        # Serialize the response data
        serializer = DayGroupSerializer(data=final_response, many=True)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)

    def get_queryset(self):
        thirty_days_ago = now() - timedelta(days=30)
        return super().get_queryset().filter(timestamp__gte=thirty_days_ago)


class StatsCreatedUsersView(generics.RetrieveAPIView):
    serializer_class = StatsCreatedUsersSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return User.objects.all()

    @method_decorator(cache_page(30))
    def get(self, request):
        stats = calculate_monthly_stats(
            self.get_queryset(),
            "date_joined",
            "total_users_joined",
            exclude_staff_filter=(Q(is_staff=True) | Q(is_superuser=True)),
        )
        return response.Response(stats)


class StatsCreatedAPIKeysView(generics.RetrieveAPIView):
    serializer_class = StastsAPIKeysCreateSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return APIKey.objects.all()

    @method_decorator(cache_page(30))
    def get(self, request, *args, **kwargs):
        stats = calculate_monthly_stats(
            self.get_queryset(),
            "created_at",
            "total_api_keys_created",
            exclude_staff_filter=(Q(user__is_staff=True) | Q(user__is_superuser=True)),
        )
        return response.Response(stats)


class StastsAPICallView(generics.RetrieveAPIView):
    serializer_class = StastsAPICallSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return APIKeyLog.objects.all()

    @method_decorator(cache_page(30))
    def get(self, request, *args, **kwargs):
        stats = calculate_monthly_stats(
            self.get_queryset(),
            "timestamp",
            "total_api_calls",
            exclude_staff_filter=(
                Q(api_key__user__is_staff=True) | Q(api_key__user__is_superuser=True)
            ),
        )

        return response.Response(stats)


class StastsSuccessActionsView(generics.RetrieveAPIView):
    serializer_class = StastsSuccessActionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return APIKeyLog.objects.all()

    @method_decorator(cache_page(30))
    def get(self, request, *args, **kwargs):

        stats = calculate_monthly_stats(
            self.get_queryset(),
            "timestamp",
            "total_successfull_actions",
            status_filter={"status": APIKeyLogStatus.SUCCESS},
            exclude_staff_filter=(
                Q(api_key__user__is_staff=True) | Q(api_key__user__is_superuser=True)
            ),
        )
        return response.Response(stats)
