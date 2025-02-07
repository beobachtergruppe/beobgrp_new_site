# Docker run:
# docker run -v /path/to/local/db.sqlite3:/app/db.sqlite3 -p 8000:8000 your_image_name

# Use an official Python runtime based on Debian 10 "buster" as a parent image.
FROM python:3.12.8-bookworm AS builder

# Get the database password from the build argument
ENV WAGTAIL_DB_PASSWORD=${WAGTAIL_DB_PASSWORD}

# Get the site init mode from an environment variable
# The value may be 'migrate' or 'restore'
ENV SITE_INIT_MODE=${SITE_INIT_MODE}

# Host of the postgres container in the docker network
ENV WAGTAIL_DB_HOST=postgres

# Directory with the site_backup. This must be mounted in docker compose
ENV DJANGO_BACKUP_DIR=/site_backup

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
    wget \
    gnupg \
    lsb-release

# Install Postgres 14 from a dedicated repository
RUN wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /usr/share/keyrings/pgdg.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/pgdg.gpg] http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update --yes --quiet && apt-get install postgresql-client-14 --yes --quiet \
    && rm -rf /var/lib/apt/lists/*

# Install the german locale
RUN apt-get update && apt-get install -y locales \
&& sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen \
&& locale-gen de_DE.UTF-8
ENV LANG=de_DE.UTF-8
ENV LANGUAGE=de_DE:de
ENV LC_ALL=de_DE.UTF-8

# Install the application server.
RUN pip install "gunicorn==20.0.4"

# Install the project requirements.
COPY requirements.txt /
RUN pip install -r /requirements.txt

# Use /app folder as a directory where the source code is stored.
WORKDIR /app

# Create media directory
RUN mkdir -p /app/media

# Set this directory to be owned by the "wagtail" user. This Wagtail project
# uses SQLite, the folder needs to be owned by the user that
# will be writing to the database file.
RUN chown -R wagtail:wagtail /app

# Copy the source code of the project into the container.
COPY --chown=wagtail:wagtail . .

# Use user "wagtail" to run the build commands below and the server itself.
USER wagtail

# Collect static files.
RUN python manage.py collectstatic --noinput --clear

# Run entrypoint script, which may perform a database migration or restore
ENTRYPOINT ./docker_entry_point.sh
