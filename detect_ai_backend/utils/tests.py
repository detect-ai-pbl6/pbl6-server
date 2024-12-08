import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase

# Assuming the function is in detect_ai_backend.utils.gcp_storage
from detect_ai_backend.utils.gcp_storage import generate_upload_signed_url_v4


class GenerateUploadSignedURLV4Test(TestCase):
    def setUp(self):
        self.valid_mime_types = [
            "image/jpeg",
            "image/png",
            "application/pdf",
            "text/plain",
            "video/mp4",
            "application/json",
        ]
        self.invalid_mime_types = ["", None, "invalid/type", "application/x-executable"]

    @patch("detect_ai_backend.utils.gcp_storage.uuid.uuid4")
    @patch("detect_ai_backend.utils.gcp_storage.settings")
    def test_generate_upload_signed_url_v4_success(self, mock_settings, mock_uuid4):
        """
        Test successful signed URL generation with various valid MIME types
        """
        for mime_type in self.valid_mime_types:
            test_uuid = uuid.UUID("12345678123456781234567812345678")
            mock_uuid4.return_value = test_uuid

            mock_blob = MagicMock()
            mock_blob.generate_signed_url.return_value = (
                f"https://mocked_signed_url.com/{mime_type}"
            )

            mock_settings.GCP_FILES_BUCKET.blob.return_value = mock_blob
            mock_settings.GCP_CREDENTIALS.service_account_email = (
                "test@example.com"  # nosec
            )
            mock_settings.GCP_CREDENTIALS.token = "mocked_access_token"  # nosec
            mock_settings.ALLOWED_UPLOAD_MIME_TYPES = self.valid_mime_types

            url, file_name = generate_upload_signed_url_v4(mime_type)

            self.assertTrue(url.startswith("https://mocked_signed_url.com/"))
            self.assertEqual(file_name, str(test_uuid))

            mock_settings.GCP_FILES_BUCKET.blob.assert_called_once_with(str(test_uuid))
            mock_blob.generate_signed_url.assert_called_once()

            mock_settings.GCP_FILES_BUCKET.blob.reset_mock()
            mock_blob.generate_signed_url.reset_mock()

    @patch("detect_ai_backend.utils.gcp_storage.settings")
    def test_generate_upload_signed_url_v4_gcp_error_handling(self, mock_settings):
        """
        Test comprehensive error handling for GCP-related exceptions
        """
        error_scenarios = [
            Exception("General GCP Error"),
            PermissionError("Authentication Failure"),
            ConnectionError("Network Connection Issue"),
        ]

        for error in error_scenarios:
            with patch(
                "detect_ai_backend.utils.gcp_storage.uuid.uuid4",
                return_value=uuid.UUID("abcdefabcdefabcdefabcdefabcdefab"),
            ):

                mock_blob = MagicMock()
                mock_blob.generate_signed_url.side_effect = error

                mock_settings.GCP_FILES_BUCKET.blob.return_value = mock_blob
                mock_settings.GCP_CREDENTIALS.service_account_email = (
                    "error_test@example.com"
                )
                mock_settings.GCP_CREDENTIALS.token = (
                    "error_mocked_access_token"  # nosec
                )
                mock_settings.ALLOWED_UPLOAD_MIME_TYPES = self.valid_mime_types

                with self.assertRaises(type(error)):
                    generate_upload_signed_url_v4("image/jpeg")

    def test_generate_upload_signed_url_v4_url_characteristics(self):
        """
        Detailed tests for generated signed URL characteristics
        """
        with patch(
            "detect_ai_backend.utils.gcp_storage.generate_upload_signed_url_v4"
        ) as mock_url_gen:
            mock_url_gen.return_value = (
                "https://example.com/signed_url",
                str(uuid.uuid4()),
            )

            url, file_name = mock_url_gen("image/jpeg")

            self.assertTrue(url.startswith("https://"))
            self.assertTrue(len(file_name) == 36)  # UUID length
            mock_url_gen.assert_called_once_with("image/jpeg")
