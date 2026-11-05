# Docker run:
# docker run -v /path/to/local/db.sqlite3:/app/db.sqlite3 -p 8000:8000 your_image_name

# Use an official Python runtime based on Debian bookworm as a parent image.
FROM python:3.15.2-bookworm

# Get the database password from the build argument
ENV WAGTAIL_DB_PASSWORD=${WAGTAIL_DB_PASSWORD}

# Get the email password from environment variable
ENV WAGTAIL_EMAIL_PASSWORD=${WAGTAIL_EMAIL_PASSWORD}

# Get the site init mode from an environment variable
# The value may be 'migrate' or 'restore'
ENV SITE_INIT_MODE=${SITE_INIT_MODE}

# Host of the postgres container in the docker network
ENV WAGTAIL_DB_HOST=postgres

# Directory with the site_backup. This must be mounted in docker compose
ENV DJANGO_BACKUP_DIR=/site_backup

# Set the media directory to the mounted volume
ENV DJANGO_MEDIA_DIR=/media


# Tell Django to use production settings
ENV PRODUCTION_VERSION=true

# Set static root for Django to match container path
ENV DJANGO_STATIC_ROOT=/app/static

# Add user that will be used in the container.
RUN useradd wagtail

# Ports used by this container to serve HTTP.
# 8000 for production, 8001 for development
EXPOSE 8000 8001

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Port is controlled by WAGTAIL_PORT environment variable in docker-compose
ENV PYTHONUNBUFFERED=1

# Install system packages required by Wagtail and Django.
# Package versions are pinned to major.minor in Debian bookworm (Debian 12), so security updates still apply.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential=12.9* \
    libpq-dev=15.19* \
    libjpeg62-turbo-dev=1:2.1* \
    zlib1g-dev=1:1.2* \
    libwebp-dev=1.2* \
    pkg-config=1.8* \
    python3-dev=3.11* \
    lsb-release=12.0* \
    nodejs=18.20* \
    npm=9.2* \
    curl=7.88* \
    ca-certificates=2025* \
    gosu=1.14*

# Install Postgres 16 from a dedicated repository
COPY dpdg.list /etc/apt/sources.list.d/
RUN install -d /usr/share/postgresql-common/pgdg && \
    curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    apt-get update && \
    apt-get install -y postgresql-client-16=16.15*

# Install the german locale
RUN apt-get update && apt-get install -y locales=2.36* \
    && sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen de_DE.UTF-8
ENV LANG=de_DE.UTF-8
ENV LANGUAGE=de_DE:de
ENV LC_ALL=de_DE.UTF-8

# Install Python dependencies
RUN pip install "pip==26.3"
RUN pip install "gunicorn==26.2.0"
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Install bulma & sass, compile CSS, then clean up
RUN npm init -y && \
    npm install --global sass@1.99.0 && \
    npm install bulma@1.0.4

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# First collect static files WITHOUT compression (creates hashed names)
# Use a temporary env var to disable compression during collectstatic
RUN COMPRESS_ENABLED=False ./manage.py collectstatic --noinput

# Now run compress - it will find the already-collected files with their hashed names
# and create the offline manifest with the correct keys
RUN ./manage.py compress

# Clean up build-time dependencies and caches
RUN apt-get update && apt-get purge -y --auto-remove \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    pkg-config \
    python3-dev \
    nodejs \
    npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Remove npm packages and cache
RUN rm -rf /usr/local/lib/node_modules /root/.npm

# The persistent media directory must also be writeable by the "wagtail" user.
RUN mkdir -p /media && chown -R wagtail:wagtail /media

# Set this directory to be owned by the "wagtail" user.
RUN chown -R wagtail:wagtail /app

# Run startup script with the provided arguments.
ENTRYPOINT ["./docker_start_server.sh"]
