from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken as JWTRefreshToken

from detect_ai_backend.authentication.models import RefreshToken, RefreshTokenFamily


def create_refresh_token(user, **kwargs):
    refresh = JWTRefreshToken.for_user(user)
    token_family = RefreshTokenFamily(user=user)
    token_family.save()
    RefreshToken(
        jti=refresh.payload[api_settings.JTI_CLAIM], family=token_family
    ).save()

    return refresh, refresh.access_token
