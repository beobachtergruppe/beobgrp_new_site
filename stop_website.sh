#!/bin/bash

# Get current git branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
IS_MAIN_BRANCH=$([ "$CURRENT_BRANCH" = "main" ] && echo true || echo false)

# Default values
STOP_DEV=false
STOP_PROD=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --dev)
      STOP_DEV=true
      shift
      ;;
    --prod)
      STOP_PROD=true
      shift
      ;;
    *)
      echo "Usage: $0 [--dev | --prod]"
      echo ""
      echo "Options:"
      echo "  --dev      Stop development server (port 8001)"
      echo "  --prod     Stop production server (port 8000) - main branch only"
      echo ""
      echo "Example:"
      echo "  $0 --prod                  # Stop production server"
      echo "  $0 --dev                   # Stop development server"
      echo ""
      echo "Current branch: $CURRENT_BRANCH"
      exit 1
      ;;
  esac
done

# Check for conflicting options
if [ "$STOP_DEV" = true ] && [ "$STOP_PROD" = true ]; then
  echo "Error: Cannot use both --dev and --prod"
  exit 1
fi

# If no option specified, prompt user
if [ "$STOP_DEV" = false ] && [ "$STOP_PROD" = false ]; then
  echo "Error: Please specify --dev or --prod"
  echo "Usage: $0 [--dev | --prod]"
  exit 1
fi

# Validate branch constraints
if [ "$STOP_PROD" = true ] && [ "$IS_MAIN_BRANCH" = false ]; then
  echo "Error: Production server can only be stopped from main branch"
  echo "Current branch: $CURRENT_BRANCH"
  exit 1
fi

PROFILE=""
if [ "$STOP_PROD" = true ]; then
  PROFILE="prod"
  echo "Stopping Production server..."
elif [ "$STOP_DEV" = true ]; then
  PROFILE="dev"
  echo "Stopping Development server..."
fi

echo "  Branch: $CURRENT_BRANCH"
echo ""

cd $(dirname $0) && docker compose --profile "$PROFILE" down

if [ $? -eq 0 ]; then
  echo ""
  if [ "$PROFILE" = "prod" ]; then
    echo "Production server stopped successfully."
  else
    echo "Development server stopped successfully."
  fi
else
  echo ""
  echo "Error: Failed to stop server."
  exit 1
fi
