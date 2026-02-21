#!/bin/bash
set -e

# Create learnflow namespace
kubectl create namespace learnflow --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

# Apply deployment
cat <<EOF | kubectl apply -f - > /dev/null 2>&1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-docs
  namespace: learnflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: learnflow-docs
  template:
    metadata:
      labels:
        app: learnflow-docs
    spec:
      containers:
      - name: docs
        image: learnflow-docs:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: learnflow-docs
  namespace: learnflow
spec:
  selector:
    app: learnflow-docs
  ports:
  - port: 80
    targetPort: 80
  type: NodePort
EOF

echo "✓ Docs deployed"
