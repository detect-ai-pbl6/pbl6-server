from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import exceptions, generics, permissions, response

from detect_ai_backend.api_keys.filters import APIKeysFilter
from detect_ai_backend.api_keys.models import APIKey, APIKeyLog, APIKeyLogStatus
from detect_ai_backend.api_keys.serializers import (
    APIKeyUpdateSerializer,
    CreateAPIKeySerializer,
    DayGroupSerializer,
    ListAPIKeySerializer,
)
from detect_ai_backend.utils.permissions import IsAuthenticationButNotAdmin


class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = APIKeysFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListAPIKeySerializer
        return CreateAPIKeySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return APIKey.objects.all().order_by("-id").select_related("user")
            self.filterset_class = None
            return (
                APIKey.objects.all()
                .order_by("-id")
                .filter(user=self.request.user)
                .select_related("user")
            )
        return APIKey.objects.none()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.is_superuser:
            raise exceptions.ParseError()
        return super().post(request, *args, **kwargs)


class APIKeyUpdateDestroyView(generics.DestroyAPIView, generics.UpdateAPIView):
    permission_classes = [IsAuthenticationButNotAdmin]
    serializer_class = APIKeyUpdateSerializer
    lookup_field = "id"
    http_method_names = ["delete", "put"]

    def get_object(self):
        return get_object_or_404(APIKey, user=self.request.user, id=self.kwargs["id"])


class APIKeyLogRetrieveView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    queryset = APIKeyLog.objects.all().order_by("-id").select_related("api_key__user")
    serializer_class = DayGroupSerializer

    def get_queryset(self):
        thirty_days_ago = now() - timedelta(days=30)
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset.filter(timestamp__gte=thirty_days_ago)
        return self.queryset.filter(
            api_key__user=self.request.user, timestamp__gte=thirty_days_ago
        )

    ALL_STATUSES = [choice[0] for choice in APIKeyLogStatus.choices]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        grouped_data = (
            queryset.annotate(day=TruncDate("timestamp"))
            .values("day", "status")
            .annotate(count=Count("id"))
        )

        response_data = {}
        for item in grouped_data:
            day = item["day"]
            if day not in response_data:
                response_data[day] = {
                    "day": day,
                    "statuses": {
                        status: 0 for status in self.ALL_STATUSES
                    },  # Initialize all statuses with 0
                }
            response_data[day]["statuses"][item["status"]] = item["count"]

        final_response = [
            {
                "day": day,
                "statuses": [
                    {"status": status, "count": count}
                    for status, count in day_data["statuses"].items()
                ],
            }
            for day, day_data in response_data.items()
        ]

        serializer = DayGroupSerializer(data=final_response, many=True)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
