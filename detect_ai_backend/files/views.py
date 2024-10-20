# Create your views here.
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, response, status

from detect_ai_backend.files.serializers import (
    SignedGCPStorageURLRequestSerializer,
    SignedGCPStorageURLResponseSerializer,
)
from detect_ai_backend.utils.gcp_storage import generate_upload_signed_url_v4


class SignedGCPStorageURLView(generics.CreateAPIView):
    serializer_class = SignedGCPStorageURLRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={status.HTTP_201_CREATED: SignedGCPStorageURLResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        url, file_name = generate_upload_signed_url_v4(validated_data["mime_type"])

        return response.Response(
            status=status.HTTP_201_CREATED,
            data={
                "upload_url": url,
                "file_url": f"{settings.GCP_STORAGE_URL}/{file_name}",
            },
        )
