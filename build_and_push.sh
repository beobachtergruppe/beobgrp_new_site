#!/bin/bash

set -e

# Default values
REGISTRY=""
BUILD_DEV=false
BUILD_PROD=false

# Function to display usage
usage() {
  echo "Usage: $0 [OPTIONS]"
  echo ""
  echo "Options:"
  echo "  -r, --registry REGISTRY    Docker registry URL (e.g., localhost:5000 or registry.example.com)"
  echo "  --dev                      Build development image"
  echo "  --prod                     Build production image"
  echo "  --both                     Build both dev and prod images"
  echo "  -h, --help                 Show this help message"
  echo ""
  echo "Examples:"
  echo "  $0 --registry localhost:5000 --dev"
  echo "  $0 --registry localhost:5000 --both"
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
    -h|--help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done

# Interactive mode if no options provided
if [ -z "$REGISTRY" ]; then
  read -p "Enter Docker registry URL (e.g., localhost:5000): " REGISTRY
fi

if [ -z "$REGISTRY" ]; then
  echo "Error: Registry URL is required"
  exit 1
fi

if [ "$BUILD_DEV" = false ] && [ "$BUILD_PROD" = false ]; then
  echo ""
  echo "What would you like to build?"
  echo "1) Development image"
  echo "2) Production image"
  echo "3) Both images"
  read -p "Enter choice (1-3): " choice
  
  case $choice in
    1)
      BUILD_DEV=true
      ;;
    2)
      BUILD_PROD=true
      ;;
    3)
      BUILD_DEV=true
      BUILD_PROD=true
      ;;
    *)
      echo "Invalid choice"
      exit 1
      ;;
  esac
fi

echo ""
echo "Registry: $REGISTRY"
echo ""

# Build and push development image
if [ "$BUILD_DEV" = true ]; then
  echo "=========================================="
  echo "Building development image..."
  echo "=========================================="
  IMAGE_NAME="$REGISTRY/beobgrp_site:1.2.2-dev"
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
  echo "Building production image..."
  echo "=========================================="
  IMAGE_NAME="$REGISTRY/beobgrp_site:1.2.2-prod"
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
