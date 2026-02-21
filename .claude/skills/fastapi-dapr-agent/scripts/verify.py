#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def verify_service(service_name):
    """Check if service pod is running"""
    result = subprocess.run(
        ['kubectl', 'get', 'pods', '-n', 'learnflow', '-l', f'app={service_name}', '-o', 'json'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ Service {service_name} not found")
        return 1

    data = json.loads(result.stdout)

    for pod in data.get('items', []):
        status = pod['status']['phase']
        if status == 'Running':
            print(f"✓ Service {service_name} running")
            return 0

    print(f"✗ Service {service_name} not ready")
    return 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("✗ Usage: verify.py <service-name>")
        sys.exit(1)

    sys.exit(verify_service(sys.argv[1]))
