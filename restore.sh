#!/bin/sh

python manage.py dbrestore --noinput --pg-options="--clean --if-exists" &&
python manage.py mediarestore --noinput &&
python manage.py migrate --noinput
