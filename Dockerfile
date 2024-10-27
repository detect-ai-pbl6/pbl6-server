# Build stage
FROM python:3.10-slim-buster AS build

WORKDIR /build

RUN apt-get update -y \
    && apt-get install -y libpq-dev gcc \
    && apt-get clean

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.10-slim-buster

WORKDIR /code

COPY --from=build /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY . .

# Set environment variables
ARG ENV

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE="detect_ai_backend.settings.production" \
    ENV=${ENV}

RUN chmod +x ./docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["./docker-entrypoint.sh"]
