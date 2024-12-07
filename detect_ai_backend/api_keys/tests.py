from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from detect_ai_backend.api_keys.models import APIKey, User


class APIKeyViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.user = User.objects.create_user(
            email="testuser@example.com", password="testpass"  # nosec
        )
        self.admin_user = User.objects.get(email=settings.SUPERUSER_EMAIL)

        # APIKey for user
        self.api_key = APIKey.objects.create(user=self.user)

    def test_api_key_list_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("list_create_api_key"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

    def test_api_key_list_unauthenticated_user(self):
        response = self.client.get(reverse("list_create_api_key"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_key_create_user(self):
        self.client.force_authenticate(user=self.user)
        payload = {"api_key_type": "free_tier"}
        response = self.client.post(reverse("list_create_api_key"), payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(APIKey.objects.count(), 2)

    def test_api_key_create_staff_user_raises_error(self):
        self.client.force_authenticate(user=self.admin_user)
        payload = {"api_key_type": "free_tier"}
        response = self.client.post(reverse("list_create_api_key"), payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_api_key_destroy(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("destroy_api_key", kwargs={"id": self.api_key.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(APIKey.objects.count(), 0)

    def test_api_key_destroy_invalid_user(self):
        other_user = User.objects.create_user(
            email="otheruser@example.com", password="otherpass"  # nosec
        )
        other_api_key = APIKey.objects.create(user=other_user)
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("destroy_api_key", kwargs={"id": other_api_key.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
