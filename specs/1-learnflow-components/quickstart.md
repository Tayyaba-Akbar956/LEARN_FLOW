# LearnFlow Deployment Quickstart

This guide shows how to deploy the complete LearnFlow stack using skills.

## Prerequisites

- Kubernetes cluster (Minikube, GKE, EKS, or AKS)
- kubectl configured
- Helm 3.x installed
- Docker installed

## Quick Deploy

Deploy the entire stack with a single command:

```bash
bash infrastructure/deploy.sh
```

This script orchestrates all skills to deploy:
1. **Infrastructure**: Kafka, PostgreSQL
2. **Backend Services**: chat, code, exercise, teacher
3. **Frontend**: Next.js application

## Manual Deployment

If you prefer to deploy components individually:

### 1. Deploy Infrastructure

```bash
# Deploy Kafka
cd .claude/skills/kafka-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py

# Deploy PostgreSQL
cd ../postgres-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py
```

### 2. Deploy Backend Services

```bash
cd ../fastapi-dapr-agent

# Chat service
python scripts/scaffold.py chat-service backend/src/api/chat.py
bash scripts/deploy.sh chat-service
python scripts/verify.py chat-service

# Code execution service
python scripts/scaffold.py code-service backend/src/api/code.py
bash scripts/deploy.sh code-service
python scripts/verify.py code-service

# Exercise service
python scripts/scaffold.py exercise-service backend/src/api/exercises.py
bash scripts/deploy.sh exercise-service
python scripts/verify.py exercise-service

# Teacher service
python scripts/scaffold.py teacher-service backend/src/api/teacher.py
bash scripts/deploy.sh teacher-service
python scripts/verify.py teacher-service
```

### 3. Deploy Frontend

```bash
cd ../nextjs-k8s-deploy
bash scripts/build.sh ../../frontend
bash scripts/load_image.sh
bash scripts/deploy.sh
python scripts/get_url.py
```

## Verification

Verify all services are running:

```bash
bash infrastructure/verify-deployment.sh
```

Expected output:
```
✅ All services verified successfully!
```

## Access the Application

Get the frontend URL:

```bash
kubectl get svc -n learnflow learnflow-frontend
```

## Troubleshooting

### Check pod status
```bash
kubectl get pods -n learnflow
```

### View logs
```bash
kubectl logs -n learnflow <pod-name>
```

### Describe pod
```bash
kubectl describe pod -n learnflow <pod-name>
```

### Check services
```bash
kubectl get svc -n learnflow
```

## Uninstall

Remove all LearnFlow components:

```bash
kubectl delete namespace learnflow
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Frontend (Next.js)            │
│  - Student Interface                    │
│  - Teacher Dashboard                    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Kong API Gateway                │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│ Backend        │  │ Infrastructure  │
│ Services       │  │                 │
│ - Chat         │  │ - Kafka         │
│ - Code         │  │ - PostgreSQL    │
│ - Exercise     │  │ - Dapr          │
│ - Teacher      │  │                 │
└────────────────┘  └─────────────────┘
```

## Skills Used

- **kafka-k8s-setup**: Deploys Kafka with KRaft mode
- **postgres-k8s-setup**: Deploys PostgreSQL with Bitnami Helm chart
- **fastapi-dapr-agent**: Scaffolds and deploys FastAPI microservices
- **nextjs-k8s-deploy**: Builds and deploys Next.js frontend

## Token Budget

All verification scripts return <50 tokens as per MCP Code Execution pattern:

```bash
# Example verification output
✅ Service: chat-service | Status: Running | Pods: 1/1
```

## Next Steps

1. Configure environment variables in each service
2. Set up monitoring and logging
3. Configure ingress for external access
4. Set up CI/CD pipelines
5. Configure backups for PostgreSQL

## Support

For issues or questions:
- Check logs: `kubectl logs -n learnflow <pod-name>`
- Review skill documentation in `.claude/skills/`
- Verify Kubernetes cluster health
