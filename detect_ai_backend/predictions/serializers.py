from rest_framework import serializers


class PredictionsSerializer(serializers.Serializer):
    image_url = serializers.URLField()
