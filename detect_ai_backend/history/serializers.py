from rest_framework import serializers

from detect_ai_backend.history.models import History


class ListHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        exclude = ["user"]
