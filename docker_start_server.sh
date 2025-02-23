#!/bin/bash

set -xe

if [ -z $SITE_INIT_MODE ]; then
  echo "Please define the SITE_INIT_MODE environment variable"
  exit 1
fi

# change user and group id of mounted volume to match the docker user
chown -R wagtail:wagtail /media

# change user to wagtail
su wagtail

# commands to configure and start the server

python manage.py collectstatic --noinput --clear

case "$SITE_INIT_MODE" in
  migrate)
    python manage.py migrate --noinput
    python manage.py migrate --noinput
    ;;
  restore)
    python manage.py migrate --noinput
    python manage.py dbrestore --noinput
    python manage.py mediarestore --noinput
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
gunicorn beobgrp_site.wsgi:application



