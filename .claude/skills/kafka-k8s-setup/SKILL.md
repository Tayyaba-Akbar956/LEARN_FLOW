---
name: kafka-k8s-setup
description: Deploys Kafka on K8s via Helm and creates topics
tags: [kafka, kubernetes, helm]
---

# kafka-k8s-setup

## When to Use
- Need Kafka for event streaming
- Setting up pub-sub infrastructure

## Instructions
1. Deploy: `bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh`
2. Verify: `python .claude/skills/kafka-k8s-setup/scripts/verify.py`
3. Create topics: `bash .claude/skills/kafka-k8s-setup/scripts/create_topics.sh`

## Validation
- [ ] Kafka pods running in kafka namespace
- [ ] All 4 LearnFlow topics created

See [REFERENCE.md](./REFERENCE.md) for details.
