from rest_framework import serializers


class StatsBase(serializers.Serializer):
    growth_percentage = serializers.FloatField()


class StatsCreatedUsersSerializer(StatsBase):

    total_users_joined = serializers.IntegerField()


class StastsAPIKeysCreateSerializer(StatsBase):

    total_api_keys_created = serializers.IntegerField()


class StastsAPICallSerializer(StatsBase):

    total_api_calls = serializers.IntegerField()


class StastsSuccessActionSerializer(StatsBase):

    total_successfull_actions = serializers.IntegerField()
