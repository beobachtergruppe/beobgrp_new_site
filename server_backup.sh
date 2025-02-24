#!/bin/sh

# Backups the databases and media and removes backups older than one week
docker exec beobgrp_new_site-wagtail-1 ./backup.sh && \
test -n $DJANGO_BACKUP_DIR && find $DJANGO_BACKUP_DIR -maxdepth 1 -mtime +3 \( -name '*.tar' -or -name '*.bin' \) -print -delete
