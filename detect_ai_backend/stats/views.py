from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import generics, permissions, response

from detect_ai_backend.api_keys.models import APIKeyLog, APIKeyLogStatus
from detect_ai_backend.api_keys.serializers import DayGroupSerializer
from detect_ai_backend.stats.serializers import StatsCreatedUsersSerializer
from detect_ai_backend.users.models import User


# Create your views here.
class StatsAPIKeyLogListView(generics.ListAPIView):
    queryset = APIKeyLog.objects.all()
    serializer_class = DayGroupSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

    ALL_STATUSES = [choice[0] for choice in APIKeyLogStatus.choices]

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

    def get(self, request):
        # Current time
        now = timezone.now()

        # Calculate current month's user count
        current_month_start = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        last_month_start = (current_month_start - timedelta(days=1)).replace(day=1)

        # Count users for current month
        current_month_users = (
            self.get_queryset()
            .filter(date_joined__gte=current_month_start, date_joined__lt=now)
            .exclude(Q(is_staff=True) | Q(is_superuser=True))
            .count()
        )
        # Count users for last month
        last_month_users = (
            self.get_queryset()
            .filter(
                date_joined__gte=last_month_start, date_joined__lt=current_month_start
            )
            .exclude(Q(is_staff=True) | Q(is_superuser=True))
            .count()
        )
        # Calculate growth percentage
        growth_percentage = 0
        if last_month_users > 0:
            growth_percentage = (
                (current_month_users - last_month_users) / last_month_users
            ) * 100

        return response.Response(
            {
                "total_users_joined": current_month_users,
                "growth_percentage": round(growth_percentage, 2),
            }
        )
