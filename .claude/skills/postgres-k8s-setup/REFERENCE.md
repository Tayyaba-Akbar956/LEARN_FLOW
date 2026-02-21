# postgres-k8s-setup Reference

## Purpose
Deploys PostgreSQL on Kubernetes using Helm and runs LearnFlow database migrations.

## How It Works

### deploy.sh
- Creates postgres namespace (idempotent)
- Adds bitnami Helm repo
- Installs postgresql chart with:
  - Username: learnflow
  - Password: learnflow123
  - Database: learnflow
  - Persistence disabled (for dev/testing)
  - --wait flag ensures pod is ready
- Prints "✓ PostgreSQL deployed"

### verify.py
- Calls kubectl get pods -n postgres -o json
- Filters to find postgresql pod
- Checks if status is Running
- Prints "✓ PostgreSQL running" or "✗ PostgreSQL not ready"

### migrate.sh
- Finds PostgreSQL pod dynamically
- Connects with: kubectl exec + psql
- Creates 3 tables:
  - **users**: id, email, role, created_at
  - **progress**: id, user_id, module, topic, mastery_score, updated_at
  - **submissions**: id, user_id, code, result, submitted_at
- Uses IF NOT EXISTS (idempotent)
- Prints "✓ Migrations applied"

## Configuration
- Namespace: postgres
- Service: postgresql.postgres.svc.cluster.local:5432
- Helm chart: bitnami/postgresql
- Credentials: learnflow / learnflow123

## Token Efficiency
- deploy.sh: all output redirected, prints only "✓ PostgreSQL deployed" (3 tokens)
- verify.py: filters JSON, prints only status (3 tokens)
- migrate.sh: SQL output hidden, prints only "✓ Migrations applied" (3 tokens)

## Usage
```bash
# Full deployment
bash .claude/skills/postgres-k8s-setup/scripts/deploy.sh
python .claude/skills/postgres-k8s-setup/scripts/verify.py
bash .claude/skills/postgres-k8s-setup/scripts/migrate.sh
```

## Troubleshooting
- If pod stuck in Pending: check Minikube resources
- If migrations fail: ensure pod is fully ready (may take 30s)
- To delete: `helm uninstall postgresql -n postgres && kubectl delete namespace postgres`

## Dependencies
- kubectl configured for Minikube
- Helm 3.x installed
- Minikube running
