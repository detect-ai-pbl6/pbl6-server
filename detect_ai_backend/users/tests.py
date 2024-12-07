from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from detect_ai_backend.users.models import User


class RegistrationAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse(
            "register"
        )  # Adjust the URL name as per your urls.py
        self.valid_payload = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "first_name": "John",
            "last_name": "Doe",
        }
        self.invalid_payload = {"email": "invalid-email", "password": "short"}

    def test_registration_success(self):
        """
        Test successful user registration
        """
        response = self.client.post(self.registration_url, self.valid_payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("Message", response.data)
        self.assertEqual(response.data["Message"], "User created successfully")

        # Verify user was actually created
        self.assertTrue(User.objects.filter(email=self.valid_payload["email"]).exists())

    def test_registration_invalid_data(self):
        """
        Test registration with invalid payload
        """
        response = self.client.post(self.registration_url, self.invalid_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RetrieveUpdateUserProfileViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",  # nosec
            first_name="Test",
            last_name="User",
        )

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        self.profile_url = reverse(
            "retrieve_update_profile"
        )  # Adjust URL name as per your urls.py

        self.update_payload = {"first_name": "Updated", "last_name": "Name"}

    def test_retrieve_user_profile(self):
        """
        Test retrieving authenticated user's profile
        """
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["first_name"], self.user.first_name)

    def test_update_user_profile_patch(self):
        """
        Test partial update (PATCH) of user profile
        """
        response = self.client.patch(self.profile_url, self.update_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.last_name, "Name")

    def test_update_user_profile_put(self):
        """
        Test full update (PUT) of user profile
        """
        full_payload = {
            "first_name": "Completely",
            "last_name": "New",
            "avatar": "tmp",
            "password": "string123",
        }
        response = self.client.put(self.profile_url, full_payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Completely")
        self.assertEqual(self.user.last_name, "New")

    def test_update_user_profile_put_failed(self):
        """
        Test full update (PUT) of user profile
        """
        full_payload = {
            "email": "newemail@example.com",
            "first_name": "Completely",
            "last_name": "New",
        }
        response = self.client.put(self.profile_url, full_payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_access(self):
        """
        Test that unauthenticated users cannot access profile
        """
        self.client.logout()
        response = self.client.get(self.profile_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ListUserViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin_user = User.objects.get(
            email=settings.SUPERUSER_EMAIL,
        )

        # Create some test users
        User.objects.create_user(
            email="user1@example.com", password="password123"
        )  # nosec
        User.objects.create_user(
            email="user2@example.com", password="password456"
        )  # nosec

        self.list_users_url = reverse(
            "list_users"
        )  # Adjust URL name as per your urls.py

    def test_list_users_by_admin(self):
        """
        Test that admin can list all users
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_users_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)  # Admin + 2 test users
        self.assertEqual(len(response.data["results"]), 3)  # Admin + 2 test users

    def test_list_users_by_non_admin(self):
        """
        Test that non-admin users are forbidden from listing users
        """
        # Create and authenticate a non-admin user
        non_admin_user = User.objects.create_user(
            email="nonadmin@example.com", password="password123"  # nosec
        )
        self.client.force_authenticate(user=non_admin_user)

        response = self.client.get(self.list_users_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_users_by_email(self):
        """
        Test filtering users by email
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_users_url, {"email": "user1@example.com"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["email"], "user1@example.com")
