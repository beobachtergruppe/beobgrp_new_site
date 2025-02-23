#!/bin/sh

python manage.py migrate --noinput
python manage.py dbrestore --noinput
python manage.py mediarestore --noinput
python manage.py migrate --noinput
