# Docker run:
# docker run -v /path/to/local/db.sqlite3:/app/db.sqlite3 -p 8000:8000 your_image_name

# Use an official Python runtime based on Debian bookworm as a parent image.
FROM python:3.12.9-bookworm

# Get the database password from the build argument
ENV WAGTAIL_DB_PASSWORD=${WAGTAIL_DB_PASSWORD}

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

# Port used by this container to serve HTTP.
EXPOSE 8000

# Set environment variables.
# 1. Force Python stdout and stderr streams to be unbuffered.
# 2. Set PORT variable that is used by Gunicorn. This should match "EXPOSE"
#    command.
ENV PYTHONUNBUFFERED=1 \
    PORT=8000

# Install system packages required by Wagtail and Django.
RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    pkg-config \
    python3-dev \
    lsb-release \
    npm \
    curl \
    ca-certificates \
    gosu

# Install Postgres 16 from a dedicated repository
COPY dpdg.list /etc/apt/sources.list.d/
RUN install -d /usr/share/postgresql-common/pgdg && \
    curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc && \
    apt-get update && \
    apt-get install -y postgresql-client-16

# Install the german locale
RUN apt-get update && apt-get install -y locales \
    && sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen de_DE.UTF-8
ENV LANG=de_DE.UTF-8
ENV LANGUAGE=de_DE:de
ENV LC_ALL=de_DE.UTF-8

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install "gunicorn==23.0.0"
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Install bulma & sass, compile CSS, then clean up
RUN npm init -y && \
    npm install --global sass && \
    npm install bulma@1.0.4

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Compress CSS/JS first (uses default StaticFilesStorage in debug mode automatically)
# Then collect static files (uses Whitenoise CompressedManifestStaticFilesStorage in production)
RUN ./manage.py compress
RUN ./manage.py collectstatic --noinput

# Clean up build-time dependencies and caches
# RUN apt-get purge -y --auto-remove \
#     build-essential \
#     libpq-dev \
#     libjpeg62-turbo-dev \
#     zlib1g-dev \
#     libwebp-dev \
#     pkg-config \
#     python3-dev \
#     npm && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Remove npm packages and cache
RUN rm -rf /usr/local/lib/node_modules /root/.npm

# The persistent media directory must also be writeable by the "wagtail" user.
RUN mkdir -p /media && chown -R wagtail:wagtail /media

# Set this directory to be owned by the "wagtail" user.
RUN chown -R wagtail:wagtail /app

# Run startup script with the provided arguments.
ENTRYPOINT ["./docker_start_server.sh"]
