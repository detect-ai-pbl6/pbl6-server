# Runtime stage
FROM python:3.10-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Set build arguments
ARG ENV

WORKDIR /code

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies in a single layer
RUN apt-get update -y \
    && apt-get install -y \
    libpq-dev \
    gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get autoremove -y \
    && apt-get clean

# Copy application code
COPY . .

# Set runtime environment variables
ENV DJANGO_SETTINGS_MODULE="detect_ai_backend.settings.production" \
    ENV=${ENV}

# Set permissions for entrypoint script
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["./docker-entrypoint.sh"]
