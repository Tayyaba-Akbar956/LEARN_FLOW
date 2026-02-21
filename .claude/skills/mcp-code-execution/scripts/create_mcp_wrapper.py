#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_wrapper(tool_name):
    """Create a new MCP wrapper script template"""

    script_path = f"scripts/{tool_name}_wrapper.py"

    template = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
MCP Code Execution Pattern Wrapper for {tool_name}

This script wraps MCP/kubectl/API calls to prevent raw JSON from entering agent context.

GOLDEN RULE:
- Never return raw API responses
- Always filter to essential information only
- Keep output under 50 tokens
\"\"\"
import subprocess
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def {tool_name}_operation():
    \"\"\"Execute {tool_name} operation and return filtered results\"\"\"

    # TODO: Replace with actual MCP/kubectl/API call
    # Example:
    # result = subprocess.run(['kubectl', 'get', 'pods', '-o', 'json'],
    #                       capture_output=True, text=True)

    # TODO: Parse and filter the response
    # data = json.loads(result.stdout)
    # Extract only what matters (pod names, status, counts, etc.)

    # TODO: Print minimal output only
    # print("✓ Operation completed")

    print("✓ {tool_name} wrapper created - implement logic above")
    return 0

if __name__ == '__main__':
    sys.exit({tool_name}_operation())
"""

    # Write template
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(template)

    print(f"✓ Created {script_path}")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("✗ Usage: create_mcp_wrapper.py <tool-name>")
        sys.exit(1)

    sys.exit(create_wrapper(sys.argv[1]))
