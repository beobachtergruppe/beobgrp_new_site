#!/bin/bash

# Get current git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
IS_MAIN_BRANCH=$([ "$CURRENT_BRANCH" = "main" ] && echo true || echo false)

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
CUSTOM_VERSION=""
PROD_VERSION=$VERSION

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      START_DEV=true
      shift
      ;;
    --version)
      CUSTOM_VERSION="$2"
      shift 2
      ;;
    --prod)
      START_PROD=true
      shift
      ;;
    migrate|restore|none)
      SITE_INIT_MODE=$1
      shift
      ;;
    *)
      echo "Usage: $0 --dev --version VERSION [migrate|restore|none]"
      echo "       $0 --prod [--version VERSION] [migrate|restore|none]"
      echo ""
      echo "Options:"
      echo "  --dev                  Start in development mode (port 8001, DEBUG=true)"
      echo "  --version VERSION      Version to use (REQUIRED for --dev, must have .dev suffix)"
      echo "  --prod                 Start in production mode (port 8000, DEBUG=false)"
      echo "                         Only available on main branch. Defaults to VERSION file."
      echo "  migrate                Run database migrations on startup"
      echo "  restore                Restore database from backup on startup"
      echo "  none                   Skip database operations (default)"
      echo ""
      echo "Examples:"
      echo "  $0 --dev --version 1.2.1.dev migrate      # Dev with specific version"
      echo "  $0 --prod migrate                         # Prod with VERSION file version"
      echo "  $0 --prod --version 1.2.0 migrate         # Prod with specific version"
      echo ""
      echo "Current branch: $CURRENT_BRANCH"
      echo "VERSION file: $VERSION"
      exit 1
      ;;
  esac
done

if [ -z "$WAGTAIL_DB_PASSWORD" ]; then
  echo Please define wagtail database password in WAGTAIL_DB_PASSWORD
  exit 1
fi

# Validate constraints
if [ "$START_PROD" = true ]; then
  if [ "$IS_MAIN_BRANCH" != true ]; then
    echo "Error: Production server can only be started from main branch"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
  fi
  # Use custom version if provided, otherwise use VERSION file
  if [ -n "$CUSTOM_VERSION" ]; then
    PROD_VERSION=$CUSTOM_VERSION
  fi
fi

if [ "$START_DEV" = true ]; then
  if [ -z "$CUSTOM_VERSION" ]; then
    echo "Error: --version is required when starting development server"
    echo "The version must have .dev suffix"
    exit 1
  fi
  if [[ ! "$CUSTOM_VERSION" =~ \.dev$ ]]; then
    echo "Error: Development version must have .dev suffix"
    echo "Provided: $CUSTOM_VERSION"
    exit 1
  fi
fi

# If no mode specified, try to default to prod (if on main branch)
if [ "$START_DEV" = false ] && [ "$START_PROD" = false ]; then
  if [ "$IS_MAIN_BRANCH" = true ]; then
    START_PROD=true
  else
    echo "Error: Must specify --dev or --prod"
    echo "Current branch: $CURRENT_BRANCH"
    echo "Production (--prod) is only available on main branch"
    exit 1
  fi
fi

if [ -z "$DOCKER_REGISTRY" ]; then
  echo "Warning: DOCKER_REGISTRY not set, using localhost:5000"
  export DOCKER_REGISTRY="localhost:5000"
fi

export SITE_INIT_MODE=$SITE_INIT_MODE
export VERSION_PROD=$PROD_VERSION
export VERSION_DEV=$CUSTOM_VERSION

# Only one mode can run at a time
PROFILE=""
if [ "$START_PROD" = true ]; then
  PROFILE="prod"
  echo "Starting Production server on port 8000"
  echo "  Version: $PROD_VERSION"
  echo "  Branch: $CURRENT_BRANCH"
elif [ "$START_DEV" = true ]; then
  PROFILE="dev"
  echo "Starting Development server on port 8001"
  echo "  Version: $CUSTOM_VERSION"
  echo "  Branch: $CURRENT_BRANCH"
fi

echo "  Registry: $DOCKER_REGISTRY"
echo "  Database operation: $SITE_INIT_MODE"
echo ""

cd $(dirname $0) && docker compose --profile "$PROFILE" up -d
