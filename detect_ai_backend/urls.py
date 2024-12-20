"""detect_ai_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenRefreshView

from detect_ai_backend.api_keys.views import (
    APIKeyListCreateView,
    APIKeyLogRetrieveView,
    APIKeyUpdateDestroyView,
)
from detect_ai_backend.authentication.views import (
    CustomTokenObtainPairView,
    JWKView,
    SocialsLoginView,
    TokenView,
)
from detect_ai_backend.files.views import SignedGCPStorageURLView
from detect_ai_backend.history.views import ListHistoryView, ListRecentHistoryView
from detect_ai_backend.predictions.views import PredictionCreateView
from detect_ai_backend.stats.views import (
    StastsAPICallView,
    StastsSuccessActionsView,
    StatsAPIKeyLogListView,
    StatsCreatedAPIKeysView,
    StatsCreatedUsersView,
)
from detect_ai_backend.users.views import (
    ListUserView,
    RegistrationAPIView,
    RetrieveUpdateUserProfileView,
    RetriveUpdateUserView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="detect_ai_backend API",
        default_version="v1",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    url=settings.HOST + "api/",
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # docs
    re_path(
        r"^docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # health
    path("api/health", lambda _: HttpResponse("OK")),
    path(".well-known/jwks.json", JWKView.as_view(), name="jwk"),
    # auth
    path("admin/", admin.site.urls),
    path("api/auth/register", RegistrationAPIView.as_view(), name="register"),
    path("api/auth/login", CustomTokenObtainPairView.as_view(), name="login"),
    path("api/auth/refresh-token", TokenRefreshView.as_view(), name="refresh_token"),
    path("api/auth/tokens", TokenView.as_view(), name="sessions_token"),
    path(
        "api/auth/login/socials",
        SocialsLoginView.as_view(),
        name="social_auth",
    ),
    path("accounts/", include("allauth.urls")),
    # Include the API endpoints:
    path("_allauth/", include("allauth.headless.urls")),
    path(
        "api/files/signed-url",
        SignedGCPStorageURLView.as_view(),
        name="files_signed_url",
    ),
    path(
        "api/users/me",
        RetrieveUpdateUserProfileView.as_view(),
        name="retrieve_update_profile",
    ),
    path(
        "api/users/<str:id>",
        RetriveUpdateUserView.as_view(),
        name="retrieve_update_single_user",
    ),
    path(
        "api/users",
        ListUserView.as_view(),
        name="list_users",
    ),
    path(
        "api/api-keys",
        APIKeyListCreateView.as_view(),
        name="list_create_api_key",
    ),
    path(
        "api/api-keys/<str:id>",
        APIKeyUpdateDestroyView.as_view(),
        name="destroy_api_key",
    ),
    path(
        "api/api-keys/<str:id>/usage",
        APIKeyLogRetrieveView.as_view(),
        name="list_create_api_key_log",
    ),
    path(
        "api/stats/api-key-logs",
        StatsAPIKeyLogListView.as_view(),
        name="list_stats_api_key_logs",
    ),
    path(
        "api/stats/users",
        StatsCreatedUsersView.as_view(),
        name="list_stats_users",
    ),
    path(
        "api/stats/api-keys",
        StatsCreatedAPIKeysView.as_view(),
        name="list_stats_api_keys",
    ),
    path(
        "api/stats/api-call",
        StastsAPICallView.as_view(),
        name="list_stats_api_call",
    ),
    path(
        "api/stats/api-call/success",
        StastsSuccessActionsView.as_view(),
        name="list_stats_api_call_success",
    ),
    path(
        "api/predictions",
        PredictionCreateView.as_view(),
        name="prediction_create_api_view",
    ),
    path(
        "api/history",
        ListHistoryView.as_view(),
        name="list_history_api_view",
    ),
    path(
        "api/history/recencies",
        ListRecentHistoryView.as_view(),
        name="list_history_api_view",
    ),
]
