# kafka-k8s-setup Reference

## Purpose
Deploys Apache Kafka on Kubernetes using Helm and creates LearnFlow topics.

## How It Works

### deploy.sh
- Creates kafka namespace (idempotent)
- Adds bitnami Helm repo
- Installs kafka chart with:
  - 1 replica (single broker)
  - KRaft mode (no Zookeeper needed)
  - Persistence disabled (for dev/testing)
  - --wait flag ensures pods are ready
- Prints "✓ Kafka deployed"

### verify.py
- Calls kubectl get pods -n kafka -o json
- Filters to count Running pods
- Expects at least 2 pods (Kafka + Zookeeper)
- Prints "✓ N Kafka pods running" or "✗ Only N pods running"

### create_topics.sh
- Finds Kafka pod dynamically
- Creates 4 topics:
  - learning.events (general learning activity)
  - code.submissions (student code runs)
  - exercise.completions (finished exercises)
  - struggle.alerts (triggers teacher notifications)
- Each topic: 1 partition, replication factor 1
- Prints "✓ Topic <name> created" for each

## Configuration
- Namespace: kafka
- Service: kafka.kafka.svc.cluster.local:9092
- Helm chart: bitnami/kafka

## Token Efficiency
- deploy.sh: all output redirected to /dev/null, prints only "✓ Kafka deployed" (3 tokens)
- verify.py: filters JSON to count, prints only summary (5 tokens)
- create_topics.sh: prints one line per topic (4 lines × 5 tokens = 20 tokens)

## Usage
```bash
# Full deployment
bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
sleep 60  # Wait for pods to stabilize
python .claude/skills/kafka-k8s-setup/scripts/verify.py
bash .claude/skills/kafka-k8s-setup/scripts/create_topics.sh
```

## Troubleshooting
- If pods stuck in Pending: check Minikube resources
- If topics fail: ensure Kafka pod is fully ready (may take 60s)
- To delete: `helm uninstall kafka -n kafka && kubectl delete namespace kafka`

## Dependencies
- kubectl configured for Minikube
- Helm 3.x installed
- Minikube running with sufficient resources (4 CPU, 8GB RAM)
