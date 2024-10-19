# Runtime stage
FROM python:3.10-slim-buster

ARG ENV
ARG SECRET_KEY
ARG CORS_ALLOWED_ORIGINS
ARG HOST

ENV PYTHONUNBUFFERED 1


WORKDIR /code

COPY . .
# RUN apk add build-base libffi-dev libstdc++ postgresql-dev libpq
RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    pip install -r requirements.txt

EXPOSE 80

ENV DJANGO_SETTINGS_MODULE="detect_ai_backend.settings.production" \
    ENV=${ENV} \
    SECRET_KEY=${SECRET_KEY}
# CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS} \
# HOST=${HOST}

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
