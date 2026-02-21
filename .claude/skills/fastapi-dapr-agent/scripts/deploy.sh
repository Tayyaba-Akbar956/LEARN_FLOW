#!/bin/bash
set -e

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
  echo "✗ Usage: deploy.sh <service-name>"
  exit 1
fi

# Build Docker image
docker build -t "${SERVICE_NAME}:latest" "services/${SERVICE_NAME}" > /dev/null 2>&1

# Load into Minikube
minikube image load "${SERVICE_NAME}:latest" > /dev/null 2>&1

# Create learnflow namespace
kubectl create namespace learnflow --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

# Apply deployment
kubectl apply -f services/${SERVICE_NAME}/k8s-deployment.yaml > /dev/null 2>&1

# Wait for pod
kubectl wait --for=condition=ready pod -l app=${SERVICE_NAME} -n learnflow --timeout=120s > /dev/null 2>&1

echo "✓ Service ${SERVICE_NAME} deployed"
