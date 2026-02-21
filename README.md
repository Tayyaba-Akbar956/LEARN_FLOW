# Skills Library

**Reusable Intelligence for Cloud-Native Mastery**

This repository contains 7 production-ready Skills that teach AI agents (Claude Code, Goose, Codex) how to autonomously deploy and manage cloud-native infrastructure.

Built for **Hackathon III** using the **MCP Code Execution Pattern**.

---

## What Are Skills?

Skills are reusable, agent-executable modules that follow this pattern:

```
SKILL.md         → Minimal instructions (~100 tokens, always loaded)
REFERENCE.md     → Deep documentation (loaded on demand)
scripts/         → Executable logic (bash/python, never loaded into context)
```

**The Golden Rule**: Scripts do the work, not the agent. All kubectl/API calls are wrapped in scripts that return minimal output (under 50 tokens), preventing token bloat and context pollution.

---

## The 7 Skills

| # | Skill | Description |
|---|---|---|
| 1 | **agents-md-gen** | Scans repo and auto-generates AGENTS.md for cross-agent compatibility |
| 2 | **kafka-k8s-setup** | Deploys Kafka on Kubernetes via Helm and creates LearnFlow topics |
| 3 | **postgres-k8s-setup** | Deploys PostgreSQL on Kubernetes and runs database migrations |
| 4 | **fastapi-dapr-agent** | Scaffolds FastAPI + Dapr microservice with K8s deployment |
| 5 | **mcp-code-execution** | Template pattern for wrapping MCP/kubectl/API calls in scripts |
| 6 | **nextjs-k8s-deploy** | Builds and deploys Next.js frontend to Kubernetes |
| 7 | **docusaurus-deploy** | Scaffolds and deploys Docusaurus documentation site |

---

## Quick Start

### Prerequisites
- Kubernetes (Minikube)
- Helm 3.x
- Docker
- kubectl
- Python 3.x
- Node.js 18+ (for frontend/docs skills)

### Using a Skill

**Via AI Agent (Claude Code, Goose):**
```
> Use the kafka-k8s-setup skill to deploy Kafka
```

**Manually:**
```bash
# Deploy Kafka
bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
python .claude/skills/kafka-k8s-setup/scripts/verify.py
bash .claude/skills/kafka-k8s-setup/scripts/create_topics.sh
```

---

## Example: Deploy Full Stack

```bash
# 1. Deploy Kafka
bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
python .claude/skills/kafka-k8s-setup/scripts/verify.py
bash .claude/skills/kafka-k8s-setup/scripts/create_topics.sh

# 2. Deploy PostgreSQL
bash .claude/skills/postgres-k8s-setup/scripts/deploy.sh
python .claude/skills/postgres-k8s-setup/scripts/verify.py
bash .claude/skills/postgres-k8s-setup/scripts/migrate.sh

# 3. Create a microservice
python .claude/skills/fastapi-dapr-agent/scripts/scaffold.py triage-agent
bash .claude/skills/fastapi-dapr-agent/scripts/deploy.sh triage-agent
python .claude/skills/fastapi-dapr-agent/scripts/verify.py triage-agent

# 4. Deploy frontend (if you have a Next.js app)
bash .claude/skills/nextjs-k8s-deploy/scripts/build.sh ./frontend
bash .claude/skills/nextjs-k8s-deploy/scripts/load_image.sh
bash .claude/skills/nextjs-k8s-deploy/scripts/deploy.sh
python .claude/skills/nextjs-k8s-deploy/scripts/get_url.py

# 5. Deploy docs
bash .claude/skills/docusaurus-deploy/scripts/scaffold.sh ./docs
bash .claude/skills/docusaurus-deploy/scripts/build.sh ./docs
bash .claude/skills/docusaurus-deploy/scripts/deploy.sh
python .claude/skills/docusaurus-deploy/scripts/get_url.py
```

---

## The MCP Code Execution Pattern

### The Problem
Direct MCP/kubectl calls flood agent context with raw JSON (10,000+ tokens), causing:
- Token waste
- Slower responses
- Context limit issues

### The Solution
Wrap all operations in scripts that filter output:

**❌ Bad (Direct Call):**
```bash
kubectl get pods -n kafka -o json
# Returns 10,000+ tokens of JSON
```

**✅ Good (Script Wrapper):**
```bash
python scripts/verify.py kafka
# Returns: ✓ 3 Kafka pods running (5 tokens)
```

**Token savings: 99.95%**

---

## Architecture

### Kubernetes Namespaces
- `kafka` - Kafka broker + Zookeeper
- `postgres` - PostgreSQL instance
- `learnflow` - All LearnFlow app services
- `dapr-system` - Dapr control plane

### Kafka Topics (LearnFlow)
- `learning.events` - General learning activity
- `code.submissions` - Student code runs
- `exercise.completions` - Finished exercises
- `struggle.alerts` - Triggers teacher notifications

### Database Schema (LearnFlow)
- `users` - User accounts and roles
- `progress` - Learning progress tracking
- `submissions` - Code submission history

---

## Adding a New Skill

1. Create skill directory:
```bash
mkdir -p .claude/skills/my-skill/scripts
```

2. Create `SKILL.md` (under 100 tokens):
```markdown
---
name: my-skill
description: One line description
tags: [tag1, tag2]
---

# my-skill

## When to Use
- Trigger condition

## Instructions
1. Run: `bash .claude/skills/my-skill/scripts/deploy.sh`

## Validation
- [ ] Check something

See [REFERENCE.md](./REFERENCE.md) for details.
```

3. Create `REFERENCE.md` with detailed documentation

4. Create scripts in `scripts/` folder:
```bash
#!/bin/bash
set -e
# Do the work...
echo "✓ Task completed"  # Minimal output only
```

5. Test manually before committing

---

## Tech Stack

- **Kubernetes (Minikube)** - Container orchestration
- **Helm** - K8s package manager
- **Kafka (Bitnami)** - Event streaming
- **PostgreSQL (Bitnami)** - Database
- **Dapr** - Microservice runtime
- **FastAPI** - Python backend framework
- **Next.js** - React frontend framework
- **Docusaurus** - Documentation site

---

## Troubleshooting

### Minikube Issues
```bash
minikube delete && minikube start --cpus=4 --memory=8192 --driver=docker
```

### Helm Chart Issues
```bash
helm repo update
helm search repo bitnami/<chart> --versions
```

### Pod Stuck in Pending
```bash
kubectl describe pod <pod-name> -n <namespace>
```

### Skill Not Recognized
- Check: `SKILL.md` must be at `.claude/skills/<name>/SKILL.md`
- Check: YAML frontmatter must start and end with `---`

---

## Commit Message Format

All commits reflect the agentic workflow:

```
Claude: created kafka-k8s-setup skill with MCP code execution pattern
Claude: created all 7 skills in .claude/skills/
Goose: verified kafka-k8s-setup skill deploys successfully
Claude: fixed postgres migration script
```

---

## Project Structure

```
skills-library/
├── CLAUDE.md                    # Instructions for Claude Code
├── AGENTS.md                    # Cross-agent context (auto-generated)
├── README.md                    # This file
├── .claude/
│   └── skills/                  # All 7 skills
│       ├── agents-md-gen/
│       ├── kafka-k8s-setup/
│       ├── postgres-k8s-setup/
│       ├── fastapi-dapr-agent/
│       ├── mcp-code-execution/
│       ├── nextjs-k8s-deploy/
│       └── docusaurus-deploy/
├── .specify/                    # Spec-Kit Plus specs
│   └── memory/
└── docs/                        # Documentation
```

---

## License

MIT

---

## Contributing

1. Follow the MCP Code Execution pattern
2. Keep SKILL.md under 100 tokens
3. All scripts must return minimal output (under 50 tokens)
4. Test manually before submitting
5. Use conventional commit messages

---

**Built with ❤️ for Hackathon III: Reusable Intelligence and Cloud-Native Mastery**
