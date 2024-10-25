from authlib.jose import JsonWebKey
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from rest_framework import authentication, permissions, response, status, views
from rest_framework_simplejwt.views import TokenObtainPairView

from detect_ai_backend.authentication.serializers import (
    CustomTokenObtainPairResponseSerializer,
)
from detect_ai_backend.utils.tokens import create_refresh_token


class CustomTokenObtainPairView(TokenObtainPairView):
    @swagger_auto_schema(
        responses={status.HTTP_200_OK: CustomTokenObtainPairResponseSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class JWKView(views.APIView):
    schema = None

    def get(self, _):
        key = JsonWebKey.import_key(settings.PUBLIC_KEY, {"kty": "RSA"})
        return response.Response(status=status.HTTP_200_OK, data={"keys": key})


class TokenView(views.APIView):

    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    @swagger_auto_schema(
        responses={status.HTTP_200_OK: CustomTokenObtainPairResponseSerializer}
    )
    def get(self, request, *args, **kwargs):
        refresh, access = create_refresh_token(request.user)
        request.session.flush()
        return response.Response(
            status=status.HTTP_200_OK,
            data={"refresh": str(refresh), "access": str(access)},
        )
