import datetime
import uuid

from django.conf import settings


def generate_upload_signed_url_v4(mime_type: str):
    """Generates a v4 signed URL for uploading a blob using HTTP PUT.

    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    file_name = str(uuid.uuid4())
    blob = settings.GCP_FILES_BUCKET.blob(file_name)
    url = blob.generate_signed_url(
        version="v4",
        # This URL is valid for 15 minutes
        expiration=datetime.timedelta(minutes=5),
        method="PUT",
        content_type=mime_type,
        service_account_email=settings.GCP_CREDENTIALS.service_account_email,
        access_token=settings.GCP_CREDENTIALS.token,
    )

    return url, file_name
