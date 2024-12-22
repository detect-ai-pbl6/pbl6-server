from django.conf import settings
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    PasswordField,
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.settings import api_settings

from detect_ai_backend.api_keys.models import APIKey
from detect_ai_backend.authentication.models import (
    RefreshToken,
    RefreshTokenFamily,
    RefreshTokenFamilyStatus,
    RefreshTokenStatus,
)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.EmailField(write_only=True)
        self.fields["password"] = PasswordField()

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        token_family = RefreshTokenFamily(user=self.user)
        token_family.save()
        RefreshToken(
            jti=refresh.payload[api_settings.JTI_CLAIM], family=token_family
        ).save()

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        is_admin = False
        if self.context["request"].headers.get("Origin", "") == settings.ADMIN_ORIGIN:
            if self.user.is_staff or self.user.is_superuser:
                is_admin = True

            if not is_admin:
                data["access"] = ""
                data["refresh"] = ""

        data["is_admin"] = is_admin

        api_key = ""
        try:
            api_key_instance = APIKey.objects.get(user=self.user, is_active=True)
            api_key = api_key_instance.api_key
        except APIKey.DoesNotExist:
            pass

        data["api_key"] = api_key
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = self.token_class(attrs["refresh"])

        refresh_token_obj = (
            RefreshToken.objects.filter(jti=refresh.payload[api_settings.JTI_CLAIM])
            .select_related("family")
            .first()
        )

        if not refresh_token_obj:
            raise TokenError(_("Refresh token is not found"))

        if refresh_token_obj.status != RefreshTokenStatus.New:
            refresh_token_obj.family.status = RefreshTokenFamilyStatus.Inactive
            refresh_token_obj.family.save()
            raise TokenError(_("Refresh token is inactive"))

        if refresh_token_obj.family.status != RefreshTokenFamilyStatus.Active:
            raise TokenError(_("Refresh token is inactive"))

        data = {"access": str(refresh.access_token)}

        refresh.set_jti()
        refresh.set_exp()
        refresh.set_iat()

        RefreshToken(
            jti=refresh.payload[api_settings.JTI_CLAIM],
            family=refresh_token_obj.family,
            parent=refresh_token_obj,
        ).save()

        refresh_token_obj.status = RefreshTokenStatus.Used
        refresh_token_obj.save()

        data["refresh"] = str(refresh)

        return data


class SocialProviders:
    PROVIDERS = []
    for key in settings.SOCIALACCOUNT_PROVIDERS.keys():
        PROVIDERS.append(key)


class SocialLoginSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=SocialProviders.PROVIDERS)
    callback_url = serializers.URLField()


class CustomTokenObtainPairResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    is_admin = serializers.BooleanField()
    api_key = serializers.CharField()


class GetTokensResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    api_key = serializers.CharField()
