# mcp-code-execution Reference

## Purpose
Provides the MCP Code Execution pattern — wraps any MCP/kubectl/API call in a script so only filtered results enter agent context.

## The Problem
When agents call MCP tools or kubectl directly, raw JSON responses (often 10,000+ tokens) flood the context window, causing:
- Token waste
- Slower responses
- Context limit issues
- Reduced ability to handle complex tasks

## The Solution
Wrap all MCP/kubectl/API calls in scripts that:
1. Execute the operation
2. Parse the response
3. Filter to essential information only
4. Return minimal output (under 50 tokens)

## Token Comparison

### ❌ Direct MCP Call (BAD)
```
Agent: kubectl get pods -n kafka -o json
Output: {"items": [{"metadata": {"name": "kafka-0", "namespace": "kafka",
"uid": "abc123", "resourceVersion": "456", "creationTimestamp": "2024-...",
"labels": {"app.kubernetes.io/name": "kafka", ...}, "annotations": {...}},
"spec": {"containers": [{"name": "kafka", "image": "bitnami/kafka:3.6.0",
"ports": [{"containerPort": 9092, "protocol": "TCP"}], ...}], ...},
"status": {"phase": "Running", "conditions": [...], ...}}]}

Tokens consumed: ~10,000
```

### ✅ Skills + Scripts Pattern (GOOD)
```
Agent: python scripts/verify.py kafka
Output: ✓ 3 Kafka pods running

Tokens consumed: ~5
```

**Token savings: 99.95%**

## How It Works

### mcp_client.py <namespace>
Example wrapper that:
- Calls: kubectl get pods -n <namespace> -o json
- Filters result to only: pod name + status phase
- Prints one line per pod: "✓ <name> — Running" or "✗ <name> — Pending"
- Never prints raw JSON

### create_mcp_wrapper.py <tool-name>
Scaffolds a new wrapper script with:
- Comment explaining the MCP code execution pattern
- Placeholder for the MCP/API call
- Filtering logic placeholder
- Minimal print output at the end
- Proper encoding for Windows

## Pattern Template

```python
#!/usr/bin/env python3
import subprocess, json, sys

# 1. Execute the operation
result = subprocess.run(['kubectl', 'get', 'pods', '-o', 'json'],
                      capture_output=True, text=True)

# 2. Parse the response
data = json.loads(result.stdout)

# 3. Filter to essentials only
running = sum(1 for pod in data['items'] if pod['status']['phase'] == 'Running')

# 4. Print minimal output
print(f"✓ {running} pods running")
sys.exit(0)
```

## When to Use This Pattern

Use for ANY operation that returns large responses:
- kubectl commands
- Helm operations
- API calls (REST, GraphQL)
- Database queries
- File system operations that return large listings

## Best Practices

1. **Always filter**: Never return raw responses
2. **Count, don't list**: "3 pods running" not "pod1, pod2, pod3"
3. **Use symbols**: ✓ for success, ✗ for failure
4. **One line per item**: If listing, keep it brief
5. **Exit codes**: 0 for success, 1 for failure
6. **Handle errors**: Catch and print friendly messages

## Usage Examples

```bash
# Check pods in a namespace
python .claude/skills/mcp-code-execution/scripts/mcp_client.py kafka
# Output: ✓ kafka-controller-0 — Running

# Create a new wrapper
python .claude/skills/mcp-code-execution/scripts/create_mcp_wrapper.py helm_status
# Output: ✓ Created scripts/helm_status_wrapper.py
```

## Integration with Skills

Every skill in this repo follows this pattern:
- SKILL.md: tells agent what to do (~100 tokens)
- REFERENCE.md: deep docs (loaded on demand)
- scripts/*.sh: bash that does the work (executed, not loaded)
- scripts/*.py: python that does the work (executed, not loaded)

This keeps the agent context clean and focused on decision-making, not data processing.

## Maintenance

When creating new skills:
1. Identify all MCP/kubectl/API calls
2. Wrap each in a script
3. Test that output is under 50 tokens
4. Document in REFERENCE.md
5. Update SKILL.md with script invocation

## Dependencies
- Python 3.x
- kubectl (if wrapping K8s operations)
- Appropriate CLI tools for the operation being wrapped
