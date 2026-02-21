#!/bin/bash
set -e

# Create learnflow namespace
kubectl create namespace learnflow --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

# Apply deployment
cat <<EOF | kubectl apply -f - > /dev/null 2>&1
apiVersion: apps/v1
kind: Deployment
metadata:
  name: learnflow-frontend
  namespace: learnflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: learnflow-frontend
  template:
    metadata:
      labels:
        app: learnflow-frontend
    spec:
      containers:
      - name: frontend
        image: learnflow-frontend:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: learnflow-frontend
  namespace: learnflow
spec:
  selector:
    app: learnflow-frontend
  ports:
  - port: 80
    targetPort: 3000
  type: NodePort
EOF

echo "✓ Frontend deployed"
