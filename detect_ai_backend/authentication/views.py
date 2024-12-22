from allauth.headless.socialaccount.views import RedirectToProviderView
from authlib.jose import JsonWebKey
from django.conf import settings
from django.middleware.csrf import get_token
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import (
    authentication,
    generics,
    permissions,
    response,
    status,
    views,
)
from rest_framework_simplejwt.views import TokenObtainPairView

from detect_ai_backend.api_keys.models import APIKey
from detect_ai_backend.authentication.serializers import (
    CustomTokenObtainPairResponseSerializer,
    GetTokensResponseSerializer,
    SocialLoginSerializer,
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

    @swagger_auto_schema(responses={status.HTTP_200_OK: GetTokensResponseSerializer})
    def get(self, request, *args, **kwargs):
        refresh, access = create_refresh_token(request.user)
        api_key = ""
        try:
            api_key_instance = APIKey.objects.get(user=request.user, is_active=True)
            api_key = api_key_instance.api_key
        except APIKey.DoesNotExist:
            pass
        request.session.flush()
        return response.Response(
            status=status.HTTP_200_OK,
            data={"refresh": str(refresh), "access": str(access), "api_key": api_key},
        )


class SocialsLoginView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = SocialLoginSerializer

    @swagger_auto_schema(
        operation_summary="Redirect to Oauth2 provider",
        operation_description="This endpoint redirects the client to a provider URL.",
        responses={
            status.HTTP_302_FOUND: openapi.Response(
                description="Redirect to Oauth2 provider URL",
            ),
            status.HTTP_201_CREATED: None,
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        data = {
            "provider": validated_data["provider"],
            "callback_url": validated_data["callback_url"],
            "csrfmiddlewaretoken": get_token(request) or "",
            "process": "login",
        }
        provider_request = request._request
        provider_request.POST = data
        redirect_view = RedirectToProviderView()

        return redirect_view.post(provider_request, *args, **kwargs)
