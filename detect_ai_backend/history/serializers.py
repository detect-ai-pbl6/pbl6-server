from rest_framework import serializers

from detect_ai_backend.history.models import History


class ListHistorySerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = "__all__"

    def get_user(self, obj):
        return obj.user.email
