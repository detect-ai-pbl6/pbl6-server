from rest_framework import serializers


class StatsCreatedUsersSerializer(serializers.Serializer):

    total_users_joined = serializers.IntegerField()
    growth_percentage = serializers.FloatField()
