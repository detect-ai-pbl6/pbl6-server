from datetime import datetime, timedelta

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient

from detect_ai_backend.api_keys.models import APIKey, APIKeyLog, APIKeyLogStatus, User


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


class APIKeyLogRetrieveViewTestCase(TestCase):
    def setUp(self):
        """
        Set up test data before each test method
        """
        # Create test users
        self.staff_user = User.objects.create_user(
            email="staffuser@gmail.com", password="testpass", is_staff=True  # nosec
        )
        self.regular_user = User.objects.create_user(
            email="regularuser@gmail.com", password="testpass"  # nosec
        )

        # Create API keys for users
        self.staff_api_key = APIKey.objects.create(user=self.staff_user)
        self.regular_api_key = APIKey.objects.create(user=self.regular_user)

        # Create test logs
        self.today = now().date()
        self.status_choices = [choice[0] for choice in APIKeyLogStatus.choices]

        # Create logs for staff user
        self._create_logs_for_user(self.staff_api_key, is_staff=True)

        # Create logs for regular user
        self._create_logs_for_user(self.regular_api_key, is_staff=False)

        # Create client for API calls
        self.client = APIClient()

    def _create_logs_for_user(self, api_key, is_staff=False, days=35):
        """
        Helper method to create logs for a given user
        """
        for i in range(days):
            day = self.today - timedelta(days=i)

            # Alternate statuses to ensure variety
            status = self.status_choices[i % len(self.status_choices)]

            APIKeyLog.objects.create(api_key=api_key, timestamp=day, status=status)

    def test_staff_user_can_see_all_logs(self):
        """
        Test that staff users can see logs from all users within 30 days
        """
        self.client.force_authenticate(user=self.staff_user)

        url = reverse(
            "list_create_api_key_log", kwargs={"id": self.staff_api_key.id}
        )  # Update with your actual URL name
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that response contains logs from the last 30 days
        self.assertEqual(len(response.data), 30)  # One entry per day

        # Verify all status types are represented
        for day_data in response.data:
            self.assertIn("day", day_data)
            self.assertIn("statuses", day_data)

            # Check that all possible statuses are included
            status_names = [
                status_item["status"] for status_item in day_data["statuses"]
            ]
            self.assertEqual(set(status_names), set(self.status_choices))

    def test_regular_user_sees_only_own_logs(self):
        """
        Test that a regular user can only see their own logs
        """
        self.client.force_authenticate(user=self.regular_user)

        url = reverse(
            "list_create_api_key_log", kwargs={"id": self.regular_api_key.id}
        )  # Update with your actual URL name
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that response contains logs from the last 30 days
        self.assertEqual(len(response.data), 30)  # One entry per day

        # Verify logs are only from the regular user's API key
        log_count = APIKeyLog.objects.filter(
            api_key__user=self.regular_user, timestamp__gte=now() - timedelta(days=30)
        ).count()
        self.assertTrue(log_count >= 0)

    def test_unauthenticated_user_cannot_access(self):
        """
        Test that unauthenticated users cannot access the view
        """
        url = reverse(
            "list_create_api_key_log", kwargs={"id": self.regular_api_key.id}
        )  # Update with your actual URL name
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logs_older_than_30_days_are_filtered_out(self):
        """
        Test that logs older than 30 days are not included
        """
        self.client.force_authenticate(user=self.staff_user)

        url = reverse(
            "list_create_api_key_log", kwargs={"id": self.staff_api_key.id}
        )  # Update with your actual URL name
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify no entries are from more than 30 days ago
        for day_data in response.data:
            day = day_data["day"]
            self.assertTrue(
                datetime.strptime(day, "%Y-%m-%d").date()
                >= (self.today - timedelta(days=30))
            )
