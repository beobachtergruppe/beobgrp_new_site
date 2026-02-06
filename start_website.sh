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
      if [ "$IS_MAIN_BRANCH" = true ]; then
        echo "Usage: $0 [--dev --version VERSION | --prod [--version VERSION]] [migrate|restore|none]"
        echo ""
        echo "Options (on main branch):"
        echo "  --prod                 Start in production mode (port 8000) [DEFAULT]"
        echo "  --version VERSION      Version for production (optional, uses VERSION file if not specified)"
        echo "  --dev --version VERSION Start development server for testing (requires .dev suffix)"
        echo "  migrate|restore|none   Database operation (default: none)"
      else
        echo "Usage: $0 [--version VERSION] [--dev] [migrate|restore|none]"
        echo ""
        echo "Options (on feature branch):"
        echo "  --version VERSION      Version to use (REQUIRED, must have .dev suffix) [DEFAULT if on feature branch]"
        echo "  --dev                  Start development server (optional, implied on feature branch)"
        echo "  migrate|restore|none   Database operation (default: none)"
      fi
      echo ""
      echo "Examples:"
      echo "  $0 --prod migrate                         # Start prod (main branch only)"
      echo "  $0 --dev --version 1.2.1.dev migrate      # Start dev server to test version"
      echo "  $0 --version 1.2.3.dev migrate            # Start dev (on feature branch)"
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

# Check for conflicting options
if [ "$START_DEV" = true ] && [ "$START_PROD" = true ]; then
  echo "Error: Cannot use both --dev and --prod"
  exit 1
fi

# Validate constraints and set defaults based on branch
if [ "$IS_MAIN_BRANCH" = true ]; then
  # On main branch: default to prod, but allow dev for testing
  if [ "$START_DEV" = true ]; then
    # Dev mode on main branch - requires .dev version
    if [ -z "$CUSTOM_VERSION" ]; then
      echo "Error: --version is required with --dev"
      echo "The version must have .dev suffix"
      exit 1
    fi
    if [[ ! "$CUSTOM_VERSION" =~ \.dev$ ]]; then
      echo "Error: Development version must have .dev suffix"
      echo "Provided: $CUSTOM_VERSION"
      exit 1
    fi
  elif [ "$START_PROD" = false ]; then
    # Default to prod if neither flag specified
    START_PROD=true
    if [ -n "$CUSTOM_VERSION" ]; then
      PROD_VERSION=$CUSTOM_VERSION
    fi
  else
    # Prod mode explicitly requested
    if [ -n "$CUSTOM_VERSION" ]; then
      PROD_VERSION=$CUSTOM_VERSION
    fi
  fi
else
  # On feature branch: default to dev, disallow prod
  if [ "$START_PROD" = true ]; then
    echo "Error: Production server can only be started from main branch"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
  fi
  # Default to dev mode
  START_DEV=true
  
  # Dev mode on feature branch - requires .dev version
  if [ -z "$CUSTOM_VERSION" ]; then
    echo "Error: --version is required (must have .dev suffix)"
    exit 1
  fi
  if [[ ! "$CUSTOM_VERSION" =~ \.dev$ ]]; then
    echo "Error: Development version must have .dev suffix"
    echo "Provided: $CUSTOM_VERSION"
    exit 1
  fi
fi

if [ -z "$DOCKER_REGISTRY" ]; then
  echo "Warning: DOCKER_REGISTRY not set, using 127.0.0.1:5000"
  export DOCKER_REGISTRY="127.0.0.1:5000"
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
