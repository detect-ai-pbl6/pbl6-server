from rest_framework import serializers

from detect_ai_backend.api_keys.models import APIKey


class CreateAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        exclude = ["user"]
        extra_kwargs = {
            "total_usage": {"read_only": True},
            "api_key": {"read_only": True},
            "maximum_usage": {
                "read_only": True,
            },
        }


class ListAPIKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = APIKey
        exclude = ["user"]
        extra_kwargs = {
            "total_usage": {"read_only": True},
            "api_key": {"read_only": True},
            "maximum_usage": {
                "read_only": True,
            },
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if "api_key" in representation and representation["api_key"]:
            api_key = representation["api_key"]
            representation["api_key"] = api_key[:5] + "***" + api_key[-5:]
        return representation


class StatusCountSerializer(serializers.Serializer):
    status = serializers.CharField()
    count = serializers.IntegerField()


class DayGroupSerializer(serializers.Serializer):
    day = serializers.DateField()
    statuses = StatusCountSerializer(many=True)
