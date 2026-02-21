#!/bin/bash
set -e

# Get Kafka pod name
KAFKA_POD=$(kubectl get pods -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

# Topics to create
TOPICS=("learning.events" "code.submissions" "exercise.completions" "struggle.alerts")

KAFKA_POD=$(kubectl get pods -n kafka -l app.kubernetes.io/name=kafka -o jsonpath='{.items[0].metadata.name}')

for TOPIC in "${TOPICS[@]}"; do
  kubectl exec -n kafka "$KAFKA_POD" -- kafka-topics.sh \
    --create \
    --if-not-exists \
    --topic "$TOPIC" \
    --bootstrap-server localhost:9092 \
    --partitions 1 \
    --replication-factor 1 > /dev/null 2>&1
  echo "✓ Topic $TOPIC created"
done
  