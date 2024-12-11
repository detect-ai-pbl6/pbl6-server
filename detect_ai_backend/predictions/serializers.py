from rest_framework import serializers


class PredictionsSerializers(serializers.Serializer):
    image_url = serializers.URLField()
