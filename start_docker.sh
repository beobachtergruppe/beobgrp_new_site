#!/bin/bash

if [ -z $1 ]; then
  echo "Usage: $0 migrate/restore"
  exit 1
fi
export SITE_INIT_MODE=$1

if [ -z "$WAGTAIL_DB_PASSWORD" ]; then
  echo Please define wagtail database password in WAGTAIL_DB_PASSWORD
  exit 1
fi

docker compose up -d --build
