from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from detect_ai_backend.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "password")

    def validate(self, args):
        email = args.get("email", None)
        if User.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError({"email": "email already exists"})

        return super().validate(args)

    def validate_password(self, value: str):
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 digit."
            )
        if not any(not char.isalnum() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 special letter"
            )
        if not any(char.isupper() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 upper case letter"
            )
        if not any(char.islower() for char in value):
            raise serializers.ValidationError(
                "This field must contain at least 1 lower case letter"
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "avatar",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {
                "read_only": True,
            },
        }


class UserUpdateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "avatar",
            "is_active",
            "id",
            "date_joined",
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "password",
            "id",
            "date_joined",
            "is_active",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def get_id(self, obj):
        return obj.id

    def get_date_joined(self, obj):
        return obj.date_joined

    def update(self, instance, validated_data):
        password = validated_data.get("password", "")
        if password:
            validated_data["password"] = make_password(password)
        return super().update(instance, validated_data)


class RegistrationResponseSerializer(serializers.Serializer):

    class UserFieldSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = [
                "first_name",
                "last_name",
                "email",
                "id",
            ]

    message = serializers.CharField()
    user = UserFieldSerializer()


class CreateUserResponse(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    date_joined = serializers.CharField()
    is_active = serializers.BooleanField()
