# fastapi-dapr-agent Reference

## Purpose
Scaffolds a complete FastAPI + Dapr microservice and deploys it to Kubernetes.

## How It Works

### scaffold.py <service-name>
Creates services/<service-name>/ with:

**main.py**: FastAPI app with:
- /health endpoint returning {"status": "ok", "service": "<name>"}
- /invoke POST endpoint for Dapr service invocation
- Runs on port 8000

**requirements.txt**: fastapi, uvicorn, dapr, openai

**Dockerfile**:
- FROM python:3.11-slim
- Installs requirements
- Runs main.py

**k8s-deployment.yaml**:
- Deployment with 1 replica
- Dapr sidecar annotations (enabled, app-id, app-port)
- Service (ClusterIP) on port 80 → 8000
- imagePullPolicy: Never (for Minikube)

Prints "✓ Service <name> scaffolded"

### deploy.sh <service-name>
- Builds Docker image: <service-name>:latest
- Loads image into Minikube
- Creates learnflow namespace (idempotent)
- Applies k8s-deployment.yaml
- Waits for pod to be ready (120s timeout)
- Prints "✓ Service <name> deployed"

### verify.py <service-name>
- Calls kubectl get pods -n learnflow -l app=<name> -o json
- Filters to check if pod is Running
- Prints "✓ Service <name> running" or "✗ Service <name> not ready"

## Configuration
- Namespace: learnflow
- Port: 8000 (internal), 80 (service)
- Dapr enabled with sidecar injection
- Image pull policy: Never (Minikube local images)

## Token Efficiency
- scaffold.py: prints only "✓ Service <name> scaffolded" (4 tokens)
- deploy.sh: all output redirected, prints only "✓ Service <name> deployed" (4 tokens)
- verify.py: filters JSON, prints only status (5 tokens)

## Usage
```bash
# Create triage-agent service
python .claude/skills/fastapi-dapr-agent/scripts/scaffold.py triage-agent
bash .claude/skills/fastapi-dapr-agent/scripts/deploy.sh triage-agent
python .claude/skills/fastapi-dapr-agent/scripts/verify.py triage-agent
```

## Dapr Integration
- Sidecar automatically injected via annotations
- Service-to-service invocation via Dapr
- State management and pub-sub available
- Requires Dapr control plane in dapr-system namespace

## Troubleshooting
- If build fails: check Dockerfile syntax
- If pod stuck: check Dapr control plane is running
- If image not found: ensure minikube image load succeeded
- To delete: `kubectl delete -f services/<name>/k8s-deployment.yaml`

## Dependencies
- Docker installed
- Minikube running
- kubectl configured
- Dapr control plane deployed (dapr init -k)
