#!/bin/bash
set -e

DOCS_DIR=$1

if [ -z "$DOCS_DIR" ]; then
  echo "✗ Usage: build.sh <docs-dir>"
  exit 1
fi

# Build Docker image
docker build -t learnflow-docs:latest "$DOCS_DIR" > /dev/null 2>&1

# Load into Minikube
minikube image load learnflow-docs:latest > /dev/null 2>&1

echo "✓ Docs image built and loaded"
