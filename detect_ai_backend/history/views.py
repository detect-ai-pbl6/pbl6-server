# Create your views here.
from datetime import timedelta

from django.utils.timezone import now
from rest_framework import generics, permissions

from detect_ai_backend.history.models import History
from detect_ai_backend.history.serializers import ListHistorySerializer


class ListHistoryView(generics.ListAPIView):

    serializer_class = ListHistorySerializer
    queryset = History.objects.all().order_by("-id")
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return super().get_queryset()
        elif self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.queryset.none()


class ListRecentHistoryView(ListHistoryView):

    permission_classes = [permissions.IsAdminUser]
    pagination_class = None

    def get_queryset(self):
        current_time = now()
        five_days_ago = current_time - timedelta(days=5)
        return self.queryset.filter(created_at__gte=five_days_ago)[:10]
