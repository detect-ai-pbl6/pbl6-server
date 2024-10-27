from rest_framework import serializers

from detect_ai_backend.users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=50, min_length=6)
    password = serializers.CharField(max_length=150, write_only=True)

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "password")

    def validate(self, args):
        email = args.get("email", None)
        if User.objects.filter(email__icontains=email).exists():
            raise serializers.ValidationError({"email": "email already exists"})

        return super().validate(args)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar", "password"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 8},
            "email": {
                "read_only": True,
            },
        }


class UserUpdateResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "avatar"]
