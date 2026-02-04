#!/bin/bash

set -e

SCRIPT_DIR=$(cd $(dirname "$0") && pwd)
REGISTRY_DATA_DIR="${REGISTRY_DATA_DIR:-$HOME/.docker-registry}"

# Parse arguments
RESTART=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --restart)
      RESTART=true
      shift
      ;;
    *)
      echo "Usage: $0 [--restart]"
      echo ""
      echo "Options:"
      echo "  --restart    Stop and remove old containers, then start fresh"
      exit 1
      ;;
  esac
done

echo "Starting Docker Registry with UI..."
echo ""

# Create persistent data directory if it doesn't exist
if [ ! -d "$REGISTRY_DATA_DIR" ]; then
  mkdir -p "$REGISTRY_DATA_DIR"
  echo "✓ Created registry data directory: $REGISTRY_DATA_DIR"
fi

# If restart flag is set, stop and remove old containers
if [ "$RESTART" = true ]; then
  echo "Stopping old containers..."
  cd "$SCRIPT_DIR" && docker compose -f registry-docker-compose.yml down 2>/dev/null || true
  echo "✓ Old containers stopped"
  echo ""
fi

# Start with docker-compose
cd "$SCRIPT_DIR"
docker compose -f registry-docker-compose.yml up -d

echo ""
echo "=========================================="
echo "Registry ready!"
echo "=========================================="
echo ""
echo "Registry API:     http://localhost:5000"
echo "Registry UI:      http://localhost:8080"
echo "Data location:    $REGISTRY_DATA_DIR"
echo ""
echo "List images:"
echo "  curl -s http://localhost:5000/v2/_catalog | jq '.repositories'"
echo ""
echo "To stop:"
echo "  docker compose -f registry-docker-compose.yml down"
echo ""
