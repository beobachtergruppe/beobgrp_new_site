#!/bin/sh

PGPASSWORD="${WAGTAIL_DB_PASSWORD}" psql -h "${WAGTAIL_DB_HOST:-localhost}" -U wagtail -d beobgrp_site -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" &&
python manage.py dbrestore --noinput --pg-options="--clean --if-exists" &&
python manage.py mediarestore --noinput &&
python manage.py migrate --noinput
