---
name: docusaurus-deploy
description: Scaffolds and deploys Docusaurus docs site
tags: [docusaurus, documentation, kubernetes]
---

# docusaurus-deploy

## When to Use
- Need documentation site for LearnFlow
- Setting up Docusaurus on Kubernetes

## Instructions
1. Scaffold: `bash .claude/skills/docusaurus-deploy/scripts/scaffold.sh <docs-dir>`
2. Build: `bash .claude/skills/docusaurus-deploy/scripts/build.sh <docs-dir>`
3. Deploy: `bash .claude/skills/docusaurus-deploy/scripts/deploy.sh`
4. Get URL: `python .claude/skills/docusaurus-deploy/scripts/get_url.py`

## Validation
- [ ] Docusaurus site scaffolded
- [ ] Docker image built and loaded
- [ ] Pod running in learnflow namespace

See [REFERENCE.md](./REFERENCE.md) for details.
