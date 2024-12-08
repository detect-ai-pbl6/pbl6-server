from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import exceptions, generics, permissions, response

from detect_ai_backend.api_keys.models import APIKey, APIKeyLog
from detect_ai_backend.api_keys.serializers import (
    CreateAPIKeySerializer,
    DayGroupSerializer,
    ListAPIKeySerializer,
)


class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = APIKey.objects.all()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListAPIKeySerializer
        return CreateAPIKeySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return self.queryset
            return self.queryset.filter(user=self.request.user)
        return self.queryset.none()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.is_superuser:
            raise exceptions.ParseError()
        return super().post(request, *args, **kwargs)


class APIKeyDestroyView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"

    def get_object(self):
        return get_object_or_404(APIKey, user=self.request.user, id=self.kwargs["id"])


class APIKeyLogListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "id"
    queryset = APIKeyLog.objects.all()
    serializer_class = DayGroupSerializer

    def get_queryset(self):
        thirty_days_ago = now() - timedelta(days=30)
        if self.request.user.is_staff or self.request.user.is_superuser:
            return self.queryset.filter(timestamp__gte=thirty_days_ago)
        return self.queryset.filter(
            api_key__user=self.request.user, timestamp__gte=thirty_days_ago
        )

    def get(self, request, *args, **kwargs):
        grouped_data = (
            self.queryset.annotate(day=TruncDate("timestamp"))
            .values("day", "status")
            .annotate(count=Count("id"))
        )
        response_data = {}
        for item in grouped_data:
            day = item["day"]
            if day not in response_data:
                response_data[day] = {"day": day, "statuses": []}
            response_data[day]["statuses"].append(
                {"status": item["status"], "count": item["count"]}
            )

        serializer = self.get_serializer(data=list(response_data.values()), many=True)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data)
