#!/bin/sh

# Backups the databases and media and removes backups older than one week
# Usage: ./server_backup.sh [--dev]
# Use --dev to backup from the _dev pod instead of the default pod

POD_NAME="beobgrp_new_site-wagtail-1"

# Parse arguments
for arg in "$@"; do
  case $arg in
    --dev)
      POD_NAME="beobgrp_new_site-wagtail_dev-1"
      shift
      ;;
  esac
done

docker exec "$POD_NAME" ./backup.sh && \
test -n $DJANGO_BACKUP_DIR && find $DJANGO_BACKUP_DIR -maxdepth 1 -mtime +3 \( -name '*.tar' -or -name '*.bin' \) -print -delete
