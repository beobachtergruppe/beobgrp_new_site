#!/bin/bash

if [ -z "$WAGTAIL_DB_PASSWORD" ]; then
  echo Please define wagtail database password in WAGTAIL_DB_PASSWORD
  exit 1
fi
 .\
&& docker compose up -d --build
