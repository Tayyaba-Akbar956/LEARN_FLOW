#!/bin/bash
set -e

# Load image into Minikube
minikube image load learnflow-frontend:latest > /dev/null 2>&1

echo "✓ Image loaded into Minikube"
