---
name: fastapi-dapr-agent
description: Scaffolds FastAPI + Dapr microservice
tags: [fastapi, dapr, microservices]
---

# fastapi-dapr-agent

## When to Use
- Need to create a new FastAPI microservice
- Building Dapr-enabled service for LearnFlow

## Instructions
1. Scaffold: `python .claude/skills/fastapi-dapr-agent/scripts/scaffold.py <service-name>`
2. Deploy: `bash .claude/skills/fastapi-dapr-agent/scripts/deploy.sh <service-name>`
3. Verify: `python .claude/skills/fastapi-dapr-agent/scripts/verify.py <service-name>`

## Validation
- [ ] Service directory created with all files
- [ ] Pod running in learnflow namespace

See [REFERENCE.md](./REFERENCE.md) for details.
