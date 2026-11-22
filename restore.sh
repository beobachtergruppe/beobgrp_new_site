#!/bin/sh

# Mandatory on a developer laptop: restore.sh is never run on the server.
: "${SITE_HOSTNAME:?Set SITE_HOSTNAME to localhost before running restore.sh}"
: "${SITE_PORT:?Set SITE_PORT to 8001 before running restore.sh}"

PGPASSWORD="${WAGTAIL_DB_PASSWORD}" psql -h "${WAGTAIL_DB_HOST:-localhost}" -U wagtail -d beobgrp_site -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" &&
python manage.py dbrestore --noinput --pg-options="--clean --if-exists" &&
python manage.py mediarestore --noinput &&
python manage.py migrate --noinput &&
python manage.py configure_default_site
