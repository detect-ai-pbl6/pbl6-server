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
RUN apt-get update -y \
    && apt-get -y install libpq-dev gcc \
    && pip install -r requirements.txt

EXPOSE 80

ENV DJANGO_SETTINGS_MODULE="detect_ai_backend.settings.production" \
    ENV=${ENV} \
    SECRET_KEY=${SECRET_KEY}

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
