# Build stage
FROM python:3.12 AS builder

ENV PYTHONUNBUFFERED 1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --user -r /requirements.txt

# Final stage
FROM python:3.12-slim

ENV PYTHONUNBUFFERED 1

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Set build arguments
ARG ENV
ARG SECRET_KEY
ARG DB_NAME
ARG DB_USERNAME
ARG DB_PASSWORD
ARG DB_HOST
ARG CORS_ALLOWED_ORIGINS
ARG HOST

# Set environment variables
ENV DJANGO_SETTINGS_MODULE="detect_ai_backend.settings.production"
ENV ENV=${ENV}
ENV SECRET_KEY=${SECRET_KEY}
ENV DB_NAME=${DB_NAME}
ENV DB_USERNAME=${DB_USERNAME}
ENV DB_PASSWORD=${DB_PASSWORD}
ENV DB_HOST=${DB_HOST}
ENV CORS_ALLOWED_ORIGINS=${CORS_ALLOWED_ORIGINS}
ENV HOST=${HOST}

# Copy application code
COPY . /code
WORKDIR /code

# Set permissions for entrypoint script
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 80

# Run the production server
ENTRYPOINT ["./docker-entrypoint.sh"]
