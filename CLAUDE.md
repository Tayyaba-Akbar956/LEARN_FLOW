# CLAUDE.md — Skills Library

## What This Repo Is
This is the **skills-library** repository for Hackathon III: Reusable Intelligence and Cloud-Native Mastery.

It contains reusable Skills that teach AI agents (Claude Code, Goose, Codex) how to deploy and manage cloud-native infrastructure autonomously.

**The Skills are the product.** Not the LearnFlow app — the Skills.

---

## Repo Structure

```
skills-library/
├── CLAUDE.md                        ← You are here
├── AGENTS.md                        ← Cross-agent context (Goose + Codex)
├── README.md                        ← Human-facing overview
├── .claude/
│   └── skills/                      ← All 7 skills live here
│       ├── agents-md-gen/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       ├── kafka-k8s-setup/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       ├── postgres-k8s-setup/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       ├── fastapi-dapr-agent/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       ├── mcp-code-execution/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       ├── nextjs-k8s-deploy/
│       │   ├── SKILL.md
│       │   ├── REFERENCE.md
│       │   └── scripts/
│       └── docusaurus-deploy/
│           ├── SKILL.md
│           ├── REFERENCE.md
│           └── scripts/
├── .specify/                        ← Spec-Kit Plus specs live here
│   └── memory/
│       ├── agents-md-gen-spec.md
│       ├── kafka-k8s-setup-spec.md
│       ├── postgres-k8s-setup-spec.md
│       ├── fastapi-dapr-agent-spec.md
│       ├── mcp-code-execution-spec.md
│       ├── nextjs-k8s-deploy-spec.md
│       └── docusaurus-deploy-spec.md
└── docs/
    └── skill-development-guide.md
```

---

## Your Primary Mission

You are an AI agent building **reusable Skills** using the **MCP Code Execution Pattern**.

### The Golden Rule
```
❌ NEVER load MCP tool results directly into context
✅ ALWAYS wrap MCP/kubectl/API calls in scripts
✅ ALWAYS return minimal output (under 50 tokens)
✅ ALWAYS keep SKILL.md under 100 tokens
```

### The Pattern You Must Follow (Every Single Skill)

```
SKILL.md         → tells you WHAT to do       (~100 tokens, always loaded)
REFERENCE.md     → deep docs                  (0 tokens, loaded on demand)
scripts/*.sh     → bash that does the work     (0 tokens, executed not loaded)
scripts/*.py     → python that does the work   (0 tokens, executed not loaded)
```

**Example of correct output from a script:**
```
✓ All 3 Kafka pods running
```

**Example of WRONG output (never do this):**
```json
{"items": [{"metadata": {"name": "kafka-0", "namespace": "kafka", 
"uid": "abc123", "resourceVersion": "456"...  (10,000 tokens)
```

---

## The 7 Skills You Must Build

| # | Skill Name | What It Does |
|---|---|---|
| 1 | `agents-md-gen` | Scans repo → generates AGENTS.md |
| 2 | `kafka-k8s-setup` | Deploys Kafka on K8s via Helm + creates topics |
| 3 | `postgres-k8s-setup` | Deploys PostgreSQL on K8s + runs migrations |
| 4 | `fastapi-dapr-agent` | Scaffolds FastAPI + Dapr microservice |
| 5 | `mcp-code-execution` | Template for wrapping any MCP call in a script |
| 6 | `nextjs-k8s-deploy` | Builds + deploys Next.js frontend to K8s |
| 7 | `docusaurus-deploy` | Scaffolds + deploys Docusaurus docs site |

---

## Tech Stack You're Working With

| Technology | Purpose | Docs |
|---|---|---|
| Kubernetes (Minikube) | Container orchestration | kubernetes.io |
| Helm | K8s package manager | helm.sh |
| Kafka (Bitnami) | Event streaming / pub-sub | kafka.apache.org |
| PostgreSQL (Bitnami) | Primary database | postgresql.org |
| Dapr | Microservice runtime (state, pub-sub) | dapr.io |
| FastAPI | Python backend framework | fastapi.tiangolo.com |
| Next.js | React frontend framework | nextjs.org |
| Docusaurus | Documentation site | docusaurus.io |
| Spec-Kit Plus | Spec-driven development | .specify/ folder |

---

## Kubernetes Namespaces

| Namespace | What Lives There |
|---|---|
| `kafka` | Kafka broker + Zookeeper |
| `postgres` | PostgreSQL instance |
| `learnflow` | All LearnFlow app services |
| `dapr-system` | Dapr control plane |

---

## Kafka Topics (LearnFlow)

```
learning.events       → general learning activity
code.submissions      → student code runs
exercise.completions  → finished exercises  
struggle.alerts       → triggers teacher notifications
```

---

## Database Schema (LearnFlow)

```sql
users        (id, email, role, created_at)
progress     (id, user_id, module, topic, mastery_score, updated_at)
submissions  (id, user_id, code, result, submitted_at)
```

---

## Coding Conventions

### Bash Scripts
```bash
#!/bin/bash
set -e                          # Exit on any error
# Do the work...
echo "✓ Task completed"         # Minimal output only
```

### Python Scripts
```python
#!/usr/bin/env python3
import subprocess, json, sys

# Do the work, filter results
# Only print the summary:
print("✓ All 3 pods running")
sys.exit(0)   # 0 = success, 1 = failure
```

### SKILL.md Template
```markdown
---
name: skill-name
description: One line description
tags: [tag1, tag2]
---

# skill-name

## When to Use
- Trigger condition 1
- Trigger condition 2

## Instructions
1. Step one: `bash scripts/step1.sh`
2. Step two: `python scripts/step2.py`

## Validation
- [ ] Checkbox 1
- [ ] Checkbox 2

See [REFERENCE.md](./REFERENCE.md) for details.
```

---

## How to Run / Test a Skill

```bash
# Test a skill manually
bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
python .claude/skills/kafka-k8s-setup/scripts/verify.py

# Invoke via Claude Code
> Use the kafka-k8s-setup skill to deploy Kafka

# Invoke via Goose (reads same .claude/skills/ directory)
> Deploy Kafka using the kafka-k8s-setup skill
```

---

## Commit Message Format

All commits must reflect the agentic workflow:

```
Claude: created kafka-k8s-setup skill with MCP code execution pattern
Claude: created all 7 skills in .claude/skills/
Goose: verified kafka-k8s-setup skill deploys successfully
Claude: fixed postgres migration script
```

---

## Evaluation Criteria (What Judges Care About)

| Criterion | Weight | What They Check |
|---|---|---|
| Skills Autonomy | 15% | Single prompt → running K8s deployment |
| Token Efficiency | 10% | Scripts do work, not the agent context |
| Cross-Agent Compatibility | 5% | Works on Claude Code AND Goose |
| Architecture | 20% | Correct Dapr, Kafka, K8s patterns |
| MCP Integration | 10% | MCP wrapped in scripts properly |
| Documentation | 10% | Docusaurus site deployed |
| Spec-Kit Plus Usage | 15% | Specs in .specify/memory/ drive skill creation |
| LearnFlow Completion | 15% | App built entirely via skills |

---

## DO and DON'T

| ✅ DO | ❌ DON'T |
|---|---|
| Keep SKILL.md under 100 tokens | Load full kubectl JSON into context |
| Put all logic in scripts/ | Write LearnFlow app code manually |
| Output "✓ Done" from scripts | Output raw API responses |
| Use Helm for K8s deployments | Hardcode values that should be configurable |
| Test each skill before moving on | Skip verification steps |
| Use conventional commit messages | Write vague commit messages |

---

## If Something Goes Wrong

```bash
# Minikube not starting
minikube delete && minikube start --cpus=4 --memory=8192 --driver=docker

# Helm chart failing
helm repo update
helm search repo bitnami/<chart> --versions

# Skill not recognized by Claude Code
# Check: SKILL.md must be at .claude/skills/<name>/SKILL.md
# Check: YAML frontmatter must start and end with ---

# Pod stuck in Pending
kubectl describe pod <pod-name> -n <namespace>  # Check Events section
```

---

*This file is for Claude Code. For Goose and other agents, see AGENTS.md.*