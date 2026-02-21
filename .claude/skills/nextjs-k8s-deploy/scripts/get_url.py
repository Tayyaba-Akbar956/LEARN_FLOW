#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def get_url():
    """Get frontend URL from Minikube"""

    result = subprocess.run(
        ['minikube', 'service', 'learnflow-frontend', '-n', 'learnflow', '--url'],
        capture_output=True, text=True
    )

    url = result.stdout.strip()
    if not url:
        print("✗ No URL returned — is the service running?")
        return 1

    print(f"✓ Frontend live at {url}")
    return 0

if __name__ == '__main__':
    sys.exit(get_url())
