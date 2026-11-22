#!/bin/bash

set -e

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

# Determine the actual version to build
BUILD_VERSION=$VERSION
if [ "$CURRENT_BRANCH" != "main" ] && [ -n "$CURRENT_BRANCH" ]; then
  BUILD_VERSION="${VERSION}.dev"
  echo "Building from branch '$CURRENT_BRANCH' - using development version: $BUILD_VERSION"
else
  echo "Building from main branch - using release version: $BUILD_VERSION"
fi

# Parse arguments
REGISTRY=""
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  -r, --registry REGISTRY    Docker registry URL (optional)"
      echo "  -h, --help                 Show this help message"
      echo ""
      echo "Examples:"
      echo "  $0                         # Build locally only (no push)"
      echo "  $0 -r registry.example.com # Build and push to remote registry"
      echo "  $0 -r 127.0.0.1:5000       # Build and push to local registry"
      echo ""
      echo "Version:"
      echo "  Current branch: $CURRENT_BRANCH"
      echo "  Version (from VERSION file): $VERSION"
      echo "  Build version: $BUILD_VERSION"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Determine image name
if [ -n "$REGISTRY" ]; then
  IMAGE_NAME="$REGISTRY/beobgrp_site:${BUILD_VERSION}"
else
  IMAGE_NAME="beobgrp_site:${BUILD_VERSION}"
fi

echo ""
echo "=========================================="
echo "Building Docker image"
echo "=========================================="
echo "Build version: $BUILD_VERSION"
echo "Image name: $IMAGE_NAME"
echo ""

# Build image
docker build -t "$IMAGE_NAME" .

if [ -n "$REGISTRY" ]; then
  echo ""
  echo "=========================================="
  echo "Pushing image to registry"
  echo "=========================================="
  docker push "$IMAGE_NAME"
  echo "✓ Image pushed: $IMAGE_NAME"
else
  echo ""
  echo "=========================================="
  echo "Build completed successfully!"
  echo "=========================================="
  echo "✓ Image built locally: $IMAGE_NAME"
  echo ""
  echo "To push to a registry, run:"
  echo "  $0 -r registry.example.com"
fi

echo ""
echo "Next steps:"
if [ "$IS_MAIN_BRANCH" = "true" ]; then
  echo "  ./start_website.sh migrate                    # Start production server"
else
  echo "  ./start_website.sh --version $BUILD_VERSION migrate   # Start dev server"
fi
echo ""
