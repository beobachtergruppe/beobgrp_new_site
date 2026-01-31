#!/bin/bash

set -xe

if [ -z $SITE_INIT_MODE ]; then
  echo "Please define the SITE_INIT_MODE environment variable"
  exit 1
fi

# change user and group id of mounted volume to match the docker user
chown -R wagtail:wagtail /media

# Run database migrations and start Gunicorn as the wagtail user
exec gosu wagtail bash -c '
set -xe
case "$SITE_INIT_MODE" in
  migrate)
    python manage.py migrate --noinput
    ;;
  restore)
    psql -h postgres -U wagtail -d beobgrp_site -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" &&
    python manage.py dbrestore --noinput --pg-options="--if-exists" &&
    python manage.py mediarestore --noinput &&
    python manage.py migrate --noinput
    ;;
  none)
    ;;
  *)
    echo "Error: SITE_INIT_MODE must be set to migrate, restore or none"
    exit 1
    ;;
esac

python manage.py clearsessions
gunicorn beobgrp_site.wsgi:application --bind 0.0.0.0:${WAGTAIL_PORT:-8000}
'



