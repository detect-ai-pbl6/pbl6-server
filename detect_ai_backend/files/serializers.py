from rest_framework import serializers

from detect_ai_backend.utils.constants import IMAGE_TYPE_CHOICES


class SignedGCPStorageURLResponseSerializer(serializers.Serializer):
    upload_url = serializers.CharField()
    file_url = serializers.CharField()


class SignedGCPStorageURLRequestSerializer(serializers.Serializer):
    mime_type = serializers.ChoiceField(choices=IMAGE_TYPE_CHOICES)
