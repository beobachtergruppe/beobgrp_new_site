#!/bin/bash

set -e

# Source the VERSION file
SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
if [ ! -f "$SCRIPT_DIR/VERSION" ]; then
  echo "Error: VERSION file not found in $SCRIPT_DIR"
  exit 1
fi
source "$SCRIPT_DIR/VERSION"

# Default values
REGISTRY=""
BUILD_DEV=false
BUILD_PROD=false
AUTO_START_REGISTRY=true

# Function to display usage
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -r, --registry REGISTRY    Docker registry URL (defaults to localhost:5000)"
  echo "  --no-auto-registry         Do not auto-start registry if none is provided"
  echo "  -h, --help                 Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0                         # Auto-starts localhost:5000 registry, builds image"
  echo "  $0 -r registry.example.com # Build for remote registry"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    --no-auto-registry)
      AUTO_START_REGISTRY=false
      shift
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

# Auto-start registry if it's localhost:5000 and not running
if [ "$REGISTRY" = "localhost:5000" ] && [ "$AUTO_START_REGISTRY" = true ]; then
  if ! docker ps --filter "name=registry" --filter "status=running" -q | grep -q .; then
    echo "=========================================="
    echo "Starting Docker registry at localhost:5000..."
    echo "=========================================="
    docker run -d \
      -p 5000:5000 \
      --name registry \
      --restart always \
      registry:latest > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
      echo "✓ Registry started successfully"
      echo "  Waiting for registry to be ready..."
      sleep 2
    else
      # Container might already exist but be stopped
      if docker ps -a --filter "name=registry" -q | grep -q .; then
        echo "✓ Starting existing registry container..."
        docker start registry > /dev/null
        sleep 2
      fi
    fi
    echo ""
  fi
fi

echo ""
echo "Registry: $REGISTRY"
echo ""

# Build and push image
echo "=========================================="
echo "Building Docker image (v${VERSION})..."
echo "=========================================="
IMAGE_NAME="$REGISTRY/beobgrp_site:${VERSION}"
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
echo "1. Run: ./start_website.sh --prod migrate"
echo "2. Or:  ./start_website.sh --dev migrate"
echo "3. Or:  ./start_website.sh --dev --prod migrate  (both simultaneously)"
