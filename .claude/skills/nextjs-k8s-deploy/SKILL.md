---
name: nextjs-k8s-deploy
description: Builds and deploys Next.js to K8s
tags: [nextjs, kubernetes, frontend]
---

# nextjs-k8s-deploy

## When to Use
- Need to deploy Next.js frontend to Kubernetes
- Building LearnFlow frontend

## Instructions
1. Build: `bash .claude/skills/nextjs-k8s-deploy/scripts/build.sh <app-dir>`
2. Load: `bash .claude/skills/nextjs-k8s-deploy/scripts/load_image.sh`
3. Deploy: `bash .claude/skills/nextjs-k8s-deploy/scripts/deploy.sh`
4. Get URL: `python .claude/skills/nextjs-k8s-deploy/scripts/get_url.py`

## Validation
- [ ] Docker image built
- [ ] Pod running in learnflow namespace
- [ ] Service accessible via URL

See [REFERENCE.md](./REFERENCE.md) for details.
