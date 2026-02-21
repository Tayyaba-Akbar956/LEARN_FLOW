#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def scan_repo(max_depth=2):
    """Scan repository and detect tech stack"""
    tech_stack = []
    structure = {}
    root = os.getcwd()

    # Detect tech stack from key files
    if os.path.exists('package.json'):
        tech_stack.append('Node.js/npm')
    if os.path.exists('requirements.txt'):
        tech_stack.append('Python')
    if os.path.exists('Dockerfile'):
        tech_stack.append('Docker')
    if os.path.exists('go.mod'):
        tech_stack.append('Go')
    if os.path.exists('helm') or os.path.isdir('helm'):
        tech_stack.append('Helm')
    if os.path.exists('k8s') or os.path.isdir('k8s'):
        tech_stack.append('Kubernetes')
    if os.path.exists('.claude/skills'):
        tech_stack.append('Claude Skills')
    if os.path.exists('.specify'):
        tech_stack.append('Spec-Kit Plus')

    # Build structure (max 2 levels)
    for item in os.listdir(root):
        if item.startswith('.') and item not in ['.claude', '.specify']:
            continue
        path = os.path.join(root, item)
        if os.path.isdir(path):
            structure[item] = []
            try:
                for subitem in os.listdir(path)[:5]:  # Limit to 5 items
                    structure[item].append(subitem)
            except:
                pass

    result = {
        'tech_stack': tech_stack,
        'structure': structure,
        'root': root
    }

    print(json.dumps(result))
    return 0

if __name__ == '__main__':
    sys.exit(scan_repo())
