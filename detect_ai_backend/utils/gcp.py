import datetime
import logging
import uuid

from django.conf import settings
from google.auth.exceptions import RefreshError, TransportError
from google.auth.transport import requests

logger = logging.getLogger(__name__)


def generate_upload_signed_url_v4(mime_type: str):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """

    def _generate_signed_url(file_name: str, attempts: int = 2):
        for attempt in range(attempts):
            try:
                blob = settings.GCP_FILES_BUCKET.blob(file_name)
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(minutes=5),
                    method="PUT",
                    content_type=mime_type,
                    service_account_email=settings.GCP_CREDENTIALS.service_account_email,
                    access_token=settings.GCP_CREDENTIALS.token,
                )
                return url
            except TransportError:
                if attempt < attempts:
                    try:
                        settings.GCP_CREDENTIALS.refresh(requests.Request())
                        logger.info("Credentials refreshed successfully")
                        continue
                    except RefreshError:
                        logger.error("Failed to refresh credentials")
                        break
        raise RuntimeError("Unable to generate signed URL after multiple attempts")

    file_name = str(uuid.uuid4())
    url = _generate_signed_url(file_name, attempts=3)
    return url, file_name
