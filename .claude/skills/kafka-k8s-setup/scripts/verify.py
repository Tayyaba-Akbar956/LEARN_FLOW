#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def verify_kafka():
    """Check if Kafka pods are running"""
    result = subprocess.run(
        ['kubectl', 'get', 'pods', '-n', 'kafka', '-o', 'json'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("✗ Kafka not found")
        return 1

    data = json.loads(result.stdout)
    running = 0

    for pod in data.get('items', []):
        status = pod['status']['phase']
        if status == 'Running':
            running += 1

    if running >= 1:  # Kafka + Zookeeper
        print(f"✓ {running} Kafka pods running")
        return 0
    else:
        print(f"✗ Only {running} pods running")
        return 1

if __name__ == '__main__':
    sys.exit(verify_kafka())
