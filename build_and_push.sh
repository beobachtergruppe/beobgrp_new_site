#!/bin/bash

set -e

# Get current git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

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

# Default values
REGISTRY=""
BUILD_DEV=false
BUILD_PROD=false

# Function to display usage
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -r, --registry REGISTRY    Docker registry URL (defaults to localhost:5000)"
  echo "  -h, --help                 Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                         # Build and push to localhost:5000"
  echo "  $0 -r registry.example.com # Build and push to remote registry"
  echo ""
  echo "Before using localhost:5000, start the registry with:"
  echo "  ./start_registry.sh"
  echo ""
  echo "Version:"
  echo "  Current branch: $CURRENT_BRANCH"
  echo "  BASE_VERSION (from VERSION file): $VERSION"
  echo "  Build version: $BUILD_VERSION"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Default to localhost:5000 if not specified
if [ -z "$REGISTRY" ]; then
  REGISTRY="localhost:5000"
fi

# Check if registry is available for localhost:5000
if [ "$REGISTRY" = "localhost:5000" ]; then
  if ! docker ps --filter "name=registry" --filter "status=running" -q | grep -q .; then
    echo "=========================================="
    echo "Error: Registry not running"
    echo "=========================================="
    echo ""
    echo "Please start the registry with:"
    echo "  ./start_registry.sh"
    echo ""
    exit 1
  fi
fi

echo ""
echo "Registry: $REGISTRY"
echo "Build version: $BUILD_VERSION"
echo ""

# Build and push image
echo "=========================================="
echo "Building Docker image (v${BUILD_VERSION})..."
echo "=========================================="
IMAGE_NAME="$REGISTRY/beobgrp_site:${BUILD_VERSION}"
docker build \
  -t "$IMAGE_NAME" \
  .

echo ""
echo "Pushing image to registry..."
docker push "$IMAGE_NAME"
echo "✓ Image pushed: $IMAGE_NAME"
echo ""

echo "=========================================="
echo "Build and push completed successfully!"
echo "=========================================="
echo ""
echo "Image built and pushed: $IMAGE_NAME"
echo ""
echo "Next steps:"
echo "  ./start_website.sh migrate  # On main branch"
echo "  or"
echo "  ./start_website.sh --version 1.x.x.dev migrate  # On feature branch"
