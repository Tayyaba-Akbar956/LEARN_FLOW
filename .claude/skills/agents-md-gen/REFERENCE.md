# agents-md-gen Reference

## Purpose
Auto-generates AGENTS.md file for cross-agent compatibility (Claude Code, Goose, Codex).

## How It Works

### scan_repo.py
- Walks directory tree (max 2 levels deep)
- Detects tech stack from key files:
  - package.json → Node.js/npm
  - requirements.txt → Python
  - Dockerfile → Docker
  - go.mod → Go
  - helm/ → Helm
  - k8s/ → Kubernetes
  - .claude/skills/ → Claude Skills
  - .specify/ → Spec-Kit Plus
- Returns JSON summary with tech_stack and structure

### generate_agents_md.py
- Calls scan_repo.py
- Parses JSON output
- Generates AGENTS.md with sections:
  - Project Overview
  - Tech Stack
  - Project Structure
  - Agent Instructions
  - Available Skills
  - How to Use a Skill
  - Key Conventions
- Writes to repo root
- Prints "✓ AGENTS.md generated"

## Output Format
AGENTS.md includes:
- List of all 7 skills with descriptions
- Usage examples for both CLI and agent invocation
- Kubernetes namespace conventions
- Commit message format
- MCP Code Execution pattern reminder

## Token Efficiency
- scan_repo.py returns compact JSON (~200 tokens)
- generate_agents_md.py prints only "✓ AGENTS.md generated" (3 tokens)
- No raw directory listings enter agent context

## Usage
```bash
# From repo root
python .claude/skills/agents-md-gen/scripts/generate_agents_md.py

# Expected output
✓ AGENTS.md generated
```

## Error Handling
- If scan fails, prints "✗ Scan failed" and exits with code 1
- If AGENTS.md cannot be written, Python raises IOError

## Maintenance
- Update generate_agents_md.py when adding new skills
- Keep skill list in sync with .claude/skills/ directory
