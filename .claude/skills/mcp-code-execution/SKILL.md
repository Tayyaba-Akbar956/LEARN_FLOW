---
name: mcp-code-execution
description: Template for wrapping MCP calls in scripts
tags: [mcp, pattern, template]
---

# mcp-code-execution

## When to Use
- Need to wrap kubectl/API calls to avoid token bloat
- Creating new skills that interact with K8s or APIs

## Instructions
1. Example: `python .claude/skills/mcp-code-execution/scripts/mcp_client.py <namespace>`
2. Create wrapper: `python .claude/skills/mcp-code-execution/scripts/create_mcp_wrapper.py <tool-name>`

## Validation
- [ ] Script returns minimal output (under 50 tokens)
- [ ] No raw JSON in agent context

See [REFERENCE.md](./REFERENCE.md) for details.
