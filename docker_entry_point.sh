#!/bin/bash

set -xe

if [ -z $SITE_INIT_MODE ]; then
  echo "Please define the SITE_INIT_MODE environment variable"
  exit 1
fi

case "$SITE_INIT_MODE" in
  migrate)
    python manage.py migrate --noinput
    ;;
  restore)
    python manage.py dbrestore --noinput
    python manage.py mediarestore --noinput
    ;;
  *)
    echo "Error: SITE_INIT_MODE must be set to migrate or restore"
    exit 1
    ;;
esac

gunicorn beobgrp_site.wsgi:application



