from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import response as drf_response
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class CustomTokenObtainPairViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {"email": "testuser@example.com", "password": "password"}
        self.user = User.objects.create_user(**self.user_data)
        self.login_url = reverse("login")

    def test_login_success(self):

        response = self.client.post(
            self.login_url,
            self.user_data,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_failed(self):

        response = self.client.post(
            self.login_url,
            {**self.user_data, "password": "123456"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            response.data["detail"],
            "No active account found with the given credentials",
        )


class JWKViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.jwk_url = reverse("jwk")

    def test_get_returns_jwk(self):
        response = self.client.get(self.jwk_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("keys", response.data)


class TokenViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token_url = reverse("sessions_token")
        self.user_data = {"email": "testuser@example.com", "password": "password"}
        self.user = User.objects.create_user(**self.user_data)

    def test_get_returns_token_pair(self):
        self.client.login(**self.user_data)
        response = self.client.get(self.token_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)
        self.assertIn("access", response.data)


class SocialsLoginViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.social_auth_url = reverse("social_auth")

    @patch("allauth.headless.socialaccount.views.RedirectToProviderView.post")
    def test_post_redirects_to_provider(self, mock_redirect):
        mock_redirect.return_value = drf_response.Response(status=status.HTTP_302_FOUND)
        data = {
            "provider": "google",
            "callback_url": "https://example.com/callback/",
        }
        response = self.client.post(self.social_auth_url, data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        mock_redirect.assert_called_once()

    def test_post_with_invalid_data_returns_error(self):
        response = self.client.post(self.social_auth_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
