from rest_framework import exceptions, generics, permissions

from detect_ai_backend.api_keys.models import APIKey
from detect_ai_backend.api_keys.serializers import (
    CreateAPIKeySerializer,
    ListAPIKeySerializer,
)

# Create your views here.


class APIKeyListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ListAPIKeySerializer
        return CreateAPIKeySerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return APIKey.objects.all()
            return APIKey.objects.filter(user=self.request.user)
        return APIKey.objects.none()

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        if self.request.user.is_staff or self.request.user.is_superuser:
            raise exceptions.ParseError()
        return super().post(request, *args, **kwargs)
