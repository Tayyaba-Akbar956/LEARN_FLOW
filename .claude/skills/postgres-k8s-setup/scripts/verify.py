#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def verify_postgres():
    """Check if PostgreSQL pod is running"""
    result = subprocess.run(
    ['kubectl', 'get', 'pods', '-n', 'postgres', 
     '-l', 'app.kubernetes.io/name=postgresql',
     '-o', 'json'],
    capture_output=True, text=True
)

# Then just check phase directly without name matching:
for pod in data.get('items', []):
    status = pod['status']['phase']
    if status == 'Running':
        print("✓ PostgreSQL running")
        return 0


if __name__ == '__main__':
    sys.exit(verify_postgres())
