#!/bin/bash
set -e

# Create postgres namespace
kubectl create namespace postgres --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

# Add bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami > /dev/null 2>&1
helm repo update > /dev/null 2>&1

# Install PostgreSQL
helm upgrade --install postgresql bitnami/postgresql \
  --namespace postgres \
  --set auth.username=learnflow \
  --set auth.password=learnflow123 \
  --set auth.database=learnflow \
  --set persistence.enabled=false \
  --wait \
  --timeout 5m > /dev/null 2>&1

echo "✓ PostgreSQL deployed"
