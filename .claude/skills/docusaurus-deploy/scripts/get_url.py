#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_url():
    """Get docs URL from Minikube"""

    result = subprocess.run(
        ['minikube', 'service', 'learnflow-docs', '-n', 'learnflow', '--url'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print("✗ Docs service not found")
        return 1

    url = result.stdout.strip()
    print(f"✓ Docs live at {url}")
    return 0

if __name__ == '__main__':
    sys.exit(get_url())
