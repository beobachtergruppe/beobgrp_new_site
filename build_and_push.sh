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
  echo "  -r, --registry REGISTRY    Docker registry URL (e.g., localhost:5000 or registry.example.com)"
  echo "                             If not provided and no registry is running, will auto-start one at localhost:5000"
  echo "  --dev                      Build development image variant only (v${VERSION})"
  echo "  --prod                     Build production image variant only (v${VERSION})"
  echo "  --both                     Build both dev and prod image variants (v${VERSION})"
  echo "  --no-auto-registry         Do not auto-start registry if none is provided"
  echo "  -h, --help                 Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --dev                          # Auto-starts registry, builds dev only"
  echo "  $0 --prod                         # Auto-starts registry, builds prod only"
  echo "  $0 --both                         # Auto-starts registry, builds both"
  echo "  $0 --registry registry.example.com --dev"
  exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -r|--registry)
      REGISTRY="$2"
      shift 2
      ;;
    --dev)
      BUILD_DEV=true
      shift
      ;;
    --prod)
      BUILD_PROD=true
      shift
      ;;
    --both)
      BUILD_DEV=true
      BUILD_PROD=true
      shift
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

if [ "$BUILD_DEV" = false ] && [ "$BUILD_PROD" = false ]; then
  BUILD_DEV=true
  BUILD_PROD=true
fi

echo ""
echo "Registry: $REGISTRY"
echo ""

# Build and push development image
if [ "$BUILD_DEV" = true ]; then
  echo "=========================================="
  echo "Building development image variant (v${VERSION})..."
  echo "=========================================="
  IMAGE_NAME="$REGISTRY/beobgrp_site:${VERSION}-dev"
  docker build \
    --build-arg DEVELOPMENT=true \
    -t "$IMAGE_NAME" \
    .
  
  echo ""
  echo "Pushing development image to registry..."
  docker push "$IMAGE_NAME"
  echo "✓ Development image pushed: $IMAGE_NAME"
  echo ""
fi

# Build and push production image
if [ "$BUILD_PROD" = true ]; then
  echo "=========================================="
  echo "Building production image variant (v${VERSION})..."
  echo "=========================================="
  IMAGE_NAME="$REGISTRY/beobgrp_site:${VERSION}-prod"
  docker build \
    --build-arg DEVELOPMENT=false \
    -t "$IMAGE_NAME" \
    .
  
  echo ""
  echo "Pushing production image to registry..."
  docker push "$IMAGE_NAME"
  echo "✓ Production image pushed: $IMAGE_NAME"
  echo ""
fi

echo "=========================================="
echo "Build and push completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update docker-compose environment with:"
echo "   export DOCKER_REGISTRY=$REGISTRY"
echo "2. Run: ./start_website.sh [--dev] [migrate|restore|none]"
