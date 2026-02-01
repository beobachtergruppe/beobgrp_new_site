#!/bin/bash

# Default values
SITE_INIT_MODE="none"
DEV_MODE=false
PORT=8000

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      DEV_MODE=true
      PORT=8001
      shift
      ;;
    migrate|restore|none)
      SITE_INIT_MODE=$1
      shift
      ;;
    *)
      echo "Usage: $0 [--dev] [migrate|restore|none]"
      echo ""
      echo "Options:"
      echo "  --dev              Start in development mode (port 8001, DEBUG=true)"
      echo "  migrate            Run database migrations on startup (default: none)"
      echo "  restore            Restore database from backup on startup"
      echo "  none               Skip database operations (default)"
      exit 1
      ;;
  esac
done

if [ -z "$WAGTAIL_DB_PASSWORD" ]; then
  echo Please define wagtail database password in WAGTAIL_DB_PASSWORD
  exit 1
fi

if [ -z "$DOCKER_REGISTRY" ]; then
  echo "Warning: DOCKER_REGISTRY not set, using localhost:5000"
  export DOCKER_REGISTRY="localhost:5000"
fi

export SITE_INIT_MODE=$SITE_INIT_MODE

PROFILE=$([[ "$DEV_MODE" == "true" ]] && echo "dev" || echo "prod")

echo "Starting website in ${PROFILE} mode from registry: $DOCKER_REGISTRY"
echo ""

cd $(dirname $0) && docker compose --profile "$PROFILE" up -d
