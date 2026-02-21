---
name: postgres-k8s-setup
description: Deploys PostgreSQL on K8s and runs migrations
tags: [postgresql, kubernetes, database]
---

# postgres-k8s-setup

## When to Use
- Need PostgreSQL database for LearnFlow
- Setting up persistent data storage

## Instructions
1. Deploy: `bash .claude/skills/postgres-k8s-setup/scripts/deploy.sh`
2. Verify: `python .claude/skills/postgres-k8s-setup/scripts/verify.py`
3. Migrate: `bash .claude/skills/postgres-k8s-setup/scripts/migrate.sh`

## Validation
- [ ] PostgreSQL pod running in postgres namespace
- [ ] 3 tables created (users, progress, submissions)

See [REFERENCE.md](./REFERENCE.md) for details.
