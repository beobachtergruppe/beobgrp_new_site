#!/bin/bash

# Source the VERSION file
SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
if [ ! -f "$SCRIPT_DIR/VERSION" ]; then
  echo "Error: VERSION file not found in $SCRIPT_DIR"
  exit 1
fi
source "$SCRIPT_DIR/VERSION"

# Default values
SITE_INIT_MODE="none"
START_DEV=false
START_PROD=false
DEV_VERSION=$VERSION
PROD_VERSION=$VERSION

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      START_DEV=true
      shift
      ;;
    --dev-version)
      DEV_VERSION="$2"
      shift 2
      ;;
    --prod)
      START_PROD=true
      shift
      ;;
    --prod-version)
      PROD_VERSION="$2"
      shift 2
      ;;
    migrate|restore|none)
      SITE_INIT_MODE=$1
      shift
      ;;
    *)
      echo "Usage: $0 [--dev [--dev-version VERSION]] [--prod [--prod-version VERSION]] [migrate|restore|none]"
      echo ""
      echo "Options:"
      echo "  --dev                  Start in development mode (port 8001, DEBUG=true)"
      echo "  --dev-version VERSION  Specific version for dev (default: $VERSION)"
      echo "  --prod                 Start in production mode (port 8000, DEBUG=false)"
      echo "  --prod-version VERSION Specific version for prod (default: $VERSION)"
      echo "  migrate                Run database migrations on startup"
      echo "  restore                Restore database from backup on startup"
      echo "  none                   Skip database operations (default)"
      echo ""
      echo "Examples:"
      echo "  $0 --dev migrate                        # Dev with migrations"
      echo "  $0 --prod migrate                       # Prod with migrations"
      echo "  $0 --dev --prod migrate                 # Both with migrations"
      echo "  $0 --dev --dev-version 1.2.1 migrate    # Dev v1.2.1, prod v$VERSION"
      echo "  $0 --prod --prod-version 1.2.0 migrate  # Prod v1.2.0, dev v$VERSION"
      exit 1
      ;;
  esac
done

# If no mode specified, default to prod
if [ "$START_DEV" = false ] && [ "$START_PROD" = false ]; then
  START_PROD=true
fi

if [ -z "$WAGTAIL_DB_PASSWORD" ]; then
  echo Please define wagtail database password in WAGTAIL_DB_PASSWORD
  exit 1
fi

if [ -z "$DOCKER_REGISTRY" ]; then
  echo "Warning: DOCKER_REGISTRY not set, using localhost:5000"
  export DOCKER_REGISTRY="localhost:5000"
fi

export SITE_INIT_MODE=$SITE_INIT_MODE
export VERSION_PROD=$PROD_VERSION
export VERSION_DEV=$DEV_VERSION

# Build profiles string
PROFILES=""
[ "$START_DEV" = true ] && PROFILES="dev"
[ "$START_PROD" = true ] && [ -n "$PROFILES" ] && PROFILES="${PROFILES},prod"
[ "$START_PROD" = true ] && [ -z "$PROFILES" ] && PROFILES="prod"

echo "Starting website:"
[ "$START_DEV" = true ] && echo "  - Development (port 8001) with version ${DEV_VERSION}"
[ "$START_PROD" = true ] && echo "  - Production (port 8000) with version ${PROD_VERSION}"
echo "  - Registry: $DOCKER_REGISTRY"
echo ""

cd $(dirname $0) && docker compose --profile "$PROFILES" up -d
