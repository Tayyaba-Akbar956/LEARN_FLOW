#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def mcp_client(namespace):
    result = subprocess.run(
        ['kubectl', 'get', 'pods', '-n', namespace, '-o', 'json'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ Namespace {namespace} not found")
        return 1

    data = json.loads(result.stdout)
    items = data.get('items', [])

    if not items:
        print(f"✗ No pods found in {namespace}")
        return 1

    all_running = True
    for pod in items:
        name = pod['metadata']['name']
        status = pod['status']['phase']
        if status == 'Running':
            print(f"✓ {name} — Running")
        else:
            print(f"✗ {name} — {status}")
            all_running = False

    return 0 if all_running else 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("✗ Usage: mcp_client.py <namespace>")
        sys.exit(1)

    sys.exit(mcp_client(sys.argv[1]))
