from drf_yasg import openapi


def get_api_key_header():
    return openapi.Parameter(
        name="x-api-key",
        in_=openapi.IN_HEADER,
        required=True,
        description="API Authentication Key. Provide a valid API key to authenticate and authorize access to the API endpoints.",  # noqa
        type=openapi.TYPE_STRING,
    )
