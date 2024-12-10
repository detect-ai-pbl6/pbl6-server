from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class StatsCreatedUsersViewTestCase(TestCase):
    def setUp(self):
        """
        Set up test data before each test method
        """
        # Create client for API calls
        self.client = APIClient()

        # Define the URL for the view
        self.url = reverse("list_stats_users")  # Update with your actual URL name

        # Get current time
        self.now = timezone.now()

        # Calculate current and last month's start dates
        self.current_month_start = self.now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        self.last_month_start = (self.current_month_start - timedelta(days=1)).replace(
            day=1
        )

        # Create users for current month
        self.current_month_regular_users = []
        for i in range(5):
            user = User.objects.create_user(
                email=f"current_month_user_{i}@gmail.com",  # nosec
                password="testpass",  # nosec
                date_joined=(self.current_month_start + timedelta(days=i + 1)),
            )
            self.current_month_regular_users.append(user)

        # Create an admin user
        self.admin_user = User.objects.create_user(
            email="adminuser@gmail.com",  # nosec
            password="testpass",  # nosec
            is_staff=True,
            is_superuser=True,
        )

        # Create users for last month
        self.last_month_regular_users = []
        for i in range(3):
            user = User.objects.create_user(
                email=f"last_month_user_{i}@gmail.com",  # nosec
                password="testpass",  # nosec
                date_joined=(self.last_month_start + timedelta(days=i + 1)),
            )
            self.last_month_regular_users.append(user)

        # Create staff users in current month
        self.current_month_staff_users = []
        for i in range(2):
            user = User.objects.create_user(
                email=f"current_month_staff_{i}@gmail.com",  # nosec
                password="testpass",  # nosec
                is_staff=True,
                date_joined=(self.current_month_start + timedelta(days=i + 1)),
            )
            self.current_month_staff_users.append(user)

        # Create superuser in current month
        self.current_month_superuser = User.objects.create_user(
            email="current_month_superuser@gmail.com",  # nosec
            password="testpass",  # nosec
            is_superuser=True,
            date_joined=(self.current_month_start + timedelta(days=10)),
        )

    def test_admin_user_can_access_stats(self):
        """
        Test that an admin user can access the stats view
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the number of users matches the expected count
        # Should be 5 regular users (excluding staff and superusers)
        self.assertEqual(response.data["total_users_joined"], 5)

    def test_regular_user_cannot_access_stats(self):
        """
        Test that a regular user cannot access the stats view
        """
        # Create a regular user
        regular_user = User.objects.create_user(
            email="regularuser@gmail.com",
            password="testpass",  # nosec
        )

        self.client.force_authenticate(user=regular_user)

        response = self.client.get(self.url)

        # Should return forbidden for non-admin users
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_access_stats(self):
        """
        Test that unauthenticated users cannot access the stats view
        """
        response = self.client.get(self.url)

        # Should return unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_growth_percentage_calculation(self):
        """
        Test the growth percentage calculation
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Calculate expected growth percentage
        last_month_count = len(self.last_month_regular_users)
        current_month_count = len(self.current_month_regular_users)

        expected_growth_percentage = 0
        if last_month_count > 0:
            expected_growth_percentage = (
                (current_month_count - last_month_count) / last_month_count
            ) * 100

        self.assertEqual(
            response.data["growth_percentage"].replace("+", ""),
            str(round(expected_growth_percentage, 2)),
        )

    def test_staff_and_superusers_are_excluded(self):
        """
        Test that staff and superusers are excluded from the user count
        """
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify only regular users are counted
        self.assertEqual(response.data["total_users_joined"], 5)
