from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from detect_ai_backend.users.models import User  # Adjust import as needed


class SignedGCPStorageURLViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword123",  # nosec
        )

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # URL for the signed GCP storage URL endpoint
        self.signed_url_endpoint = reverse(
            "files_signed_url"
        )  # Adjust URL name as needed

        # Valid payload for generating signed URL
        self.valid_payload = {"mime_type": "image/jpeg"}

        # Invalid payload for testing validation
        self.invalid_payload = {"mime_type": "invalid/type"}

    @patch("detect_ai_backend.files.views.generate_upload_signed_url_v4")
    def test_generate_signed_url_success(self, mock_generate_url):
        """
        Test successful generation of signed GCP storage URL
        """
        # Mock the URL generation function
        mock_generate_url.return_value = (
            "https://storage.googleapis.com/signed-url",
            "test-file-123.jpg",
        )

        response = self.client.post(self.signed_url_endpoint, self.valid_payload)

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the generated URL contains expected components
        self.assertIn("upload_url", response.data)
        self.assertIn("file_url", response.data)

        # Verify the file URL is constructed correctly
        expected_file_url = f"{settings.GCP_STORAGE_URL}/test-file-123.jpg"
        self.assertEqual(response.data["file_url"], expected_file_url)

        # Verify the mock was called with correct arguments
        mock_generate_url.assert_called_once_with(self.valid_payload["mime_type"])

    def test_unauthenticated_access(self):
        """
        Test that unauthenticated users cannot generate signed URLs
        """
        # Logout the authenticated user
        self.client.logout()

        response = self.client.post(self.signed_url_endpoint, self.valid_payload)

        # Should return unauthorized status
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("detect_ai_backend.files.views.generate_upload_signed_url_v4")
    def test_url_generation_with_different_mime_types(self, mock_generate_url):
        """
        Test URL generation with various MIME types
        """
        test_mime_types = ["image/png", "image/bmp", "image/jpeg", "image/gif"]

        for mime_type in test_mime_types:
            # Reset the mock for each iteration
            mock_generate_url.reset_mock()
            mock_generate_url.return_value = (
                "https://storage.googleapis.com/signed-url",
                f'test-file-{mime_type.replace("/", "-")}.file',
            )

            payload = {"mime_type": mime_type}
            response = self.client.post(self.signed_url_endpoint, payload)

            # Assertions
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            mock_generate_url.assert_called_once_with(mime_type)

    def test_missing_mime_type(self):
        """
        Test handling of missing MIME type in request
        """
        response = self.client.post(self.signed_url_endpoint, {})

        # Should return bad request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("mime_type", response.data)

    @patch("detect_ai_backend.files.views.generate_upload_signed_url_v4")
    def test_url_generation_failure(self, mock_generate_url):
        """
        Test handling of URL generation failure
        """
        # Simulate an exception during URL generation
        mock_generate_url.side_effect = Exception("GCP URL generation failed")

        with self.assertRaises(Exception):
            self.client.post(self.signed_url_endpoint, self.valid_payload)

    def test_serializer_validation(self):
        """
        Test serializer validation for MIME types
        """
        invalid_payloads = [
            {"mime_type": ""},  # Empty MIME type
            {"mime_type": "invalid/mime"},  # Invalid MIME type format
        ]

        for payload in invalid_payloads:
            response = self.client.post(self.signed_url_endpoint, payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
