#!/bin/bash
set -e

APP_DIR=$1

if [ -z "$APP_DIR" ]; then
  echo "✗ Usage: build.sh <app-dir>"
  exit 1
fi

# Build Docker image
docker build -t learnflow-frontend:latest "$APP_DIR" > /dev/null 2>&1

echo "✓ Image built: learnflow-frontend:latest"
