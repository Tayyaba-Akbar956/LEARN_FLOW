#!/bin/bash
set -e

# Create kafka namespace
kubectl create namespace kafka --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

# Add bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami > /dev/null 2>&1
helm repo update > /dev/null 2>&1

# Install Kafka
helm upgrade --install kafka bitnami/kafka \
  --namespace kafka \
  --set controller.replicaCount=1 \
  --set persistence.enabled=false \
  --wait \
  --timeout 5m > /dev/null 2>&1
