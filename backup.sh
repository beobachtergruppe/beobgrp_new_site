#!/bin/bash

python manage.py dbbackup && \
python manage.py mediabackup
