# Create your views here.
from rest_framework import generics, permissions

from detect_ai_backend.history.filters import HistoryFilter
from detect_ai_backend.history.models import History
from detect_ai_backend.history.serializers import ListHistorySerializer


class ListHistoryView(generics.ListAPIView):

    serializer_class = ListHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = HistoryFilter

    def get_queryset(self):
        if self.request.user.is_staff or self.request.user.is_superuser:
            return History.objects.all().order_by("-id").select_related("user")
        elif self.request.user.is_authenticated:
            self.filterset_class = None
            return (
                History.objects.filter(user=self.request.user)
                .order_by("-id")
                .select_related("user")
            )
        return History.objects.none()


class ListRecentHistoryView(ListHistoryView):

    permission_classes = [permissions.IsAdminUser]
    pagination_class = None
    queryset = History.objects.all().select_related("user")

    def get_queryset(self):
        return self.queryset.order_by("-created_at")[:7]
