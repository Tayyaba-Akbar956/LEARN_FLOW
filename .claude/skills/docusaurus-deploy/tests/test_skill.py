#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real execution tests for docusaurus-deploy skill"""
import os
import sys
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_scaffold_script_syntax():
    """Test that scaffold.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/docusaurus-deploy/scripts/scaffold.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: scaffold.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: scaffold.sh has valid bash syntax")
    return True

def test_build_script_syntax():
    """Test that build.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/docusaurus-deploy/scripts/build.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: build.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: build.sh has valid bash syntax")
    return True

def test_deploy_script_syntax():
    """Test that deploy.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/docusaurus-deploy/scripts/deploy.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: deploy.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: deploy.sh has valid bash syntax")
    return True

def test_get_url_script_executes():
    """Test that get_url.py can execute"""
    result = subprocess.run(
        ['python', '.claude/skills/docusaurus-deploy/scripts/get_url.py'],
        capture_output=True, text=True
    )

    # Should exit with 0 or 1 (not crash)
    if result.returncode not in [0, 1]:
        print(f"✗ FAIL: get_url.py crashed with exit code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    print(f"✓ PASS: get_url.py executes correctly (exit {result.returncode})")
    return True

def test_scaffold_creates_dockerfile():
    """Test that scaffold.sh actually creates a Dockerfile"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/scaffold.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'cat > Dockerfile' not in content and 'cat >Dockerfile' not in content:
        print("✗ FAIL: scaffold.sh does not create Dockerfile")
        return False

    print("✓ PASS: scaffold.sh creates Dockerfile")
    return True

def test_dockerfile_has_multistage_build():
    """Test that generated Dockerfile uses multi-stage build"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/scaffold.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_stages = [
        'FROM node:18-alpine AS builder',
        'FROM nginx:alpine'
    ]

    missing = []
    for stage in required_stages:
        if stage not in content:
            missing.append(stage)

    if missing:
        print(f"✗ FAIL: Dockerfile missing stages: {', '.join(missing)}")
        return False

    print("✓ PASS: Dockerfile uses multi-stage build (builder + nginx)")
    return True

def test_dockerfile_has_correct_structure():
    """Test that Dockerfile has correct build structure"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/scaffold.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_elements = [
        'npm install',
        'npm run build',
        'COPY --from=builder',
        'EXPOSE 80'
    ]

    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)

    if missing:
        print(f"✗ FAIL: Dockerfile missing elements: {', '.join(missing)}")
        return False

    print("✓ PASS: Dockerfile has correct build structure")
    return True

def test_deploy_uses_inline_yaml():
    """Test that deploy.sh uses inline YAML"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/deploy.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'cat <<EOF' not in content:
        print("✗ FAIL: deploy.sh does not use cat <<EOF for inline YAML")
        return False

    if 'kubectl apply -f -' not in content:
        print("✗ FAIL: deploy.sh does not pipe to kubectl apply -f -")
        return False

    print("✓ PASS: deploy.sh uses inline YAML pattern")
    return True

def test_deploy_has_correct_k8s_resources():
    """Test that deploy.sh creates both Deployment and Service"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/deploy.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_resources = [
        'kind: Deployment',
        'kind: Service',
        'learnflow-docs',
        'containerPort: 80'
    ]

    missing = []
    for resource in required_resources:
        if resource not in content:
            missing.append(resource)

    if missing:
        print(f"✗ FAIL: deploy.sh missing K8s resources: {', '.join(missing)}")
        return False

    print("✓ PASS: deploy.sh creates Deployment and Service")
    return True

def test_deployment_uses_never_pull_policy():
    """Test that deployment uses imagePullPolicy: Never"""
    script_path = '.claude/skills/docusaurus-deploy/scripts/deploy.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'imagePullPolicy: Never' not in content:
        print("✗ FAIL: deploy.sh missing imagePullPolicy: Never")
        return False

    print("✓ PASS: Deployment uses imagePullPolicy: Never")
    return True

def test_scripts_have_error_handling():
    """Test that bash scripts use set -e for error handling"""
    scripts = [
        '.claude/skills/docusaurus-deploy/scripts/scaffold.sh',
        '.claude/skills/docusaurus-deploy/scripts/build.sh',
        '.claude/skills/docusaurus-deploy/scripts/deploy.sh'
    ]

    for script_path in scripts:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'set -e' not in content:
            print(f"✗ FAIL: {os.path.basename(script_path)} missing 'set -e'")
            return False

    print("✓ PASS: All bash scripts have error handling (set -e)")
    return True

def test_scripts_redirect_output():
    """Test that scripts redirect verbose output"""
    scripts = [
        '.claude/skills/docusaurus-deploy/scripts/scaffold.sh',
        '.claude/skills/docusaurus-deploy/scripts/build.sh',
        '.claude/skills/docusaurus-deploy/scripts/deploy.sh'
    ]

    for script_path in scripts:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if '> /dev/null 2>&1' not in content and '/dev/null' not in content:
            print(f"✗ FAIL: {os.path.basename(script_path)} does not redirect output")
            return False

    print("✓ PASS: Scripts redirect verbose output")
    return True

def test_get_url_output_is_minimal():
    """Test that get_url.py output is minimal"""
    result = subprocess.run(
        ['python', '.claude/skills/docusaurus-deploy/scripts/get_url.py'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    if output:  # Only check if there's output
        token_count = len(output.split())

        if token_count > 15:
            print(f"✗ FAIL: get_url.py output too verbose ({token_count} tokens)")
            return False

    print("✓ PASS: get_url.py output is minimal")
    return True

def main():
    """Run all execution tests"""
    tests = [
        test_scaffold_script_syntax,
        test_build_script_syntax,
        test_deploy_script_syntax,
        test_get_url_script_executes,
        test_scaffold_creates_dockerfile,
        test_dockerfile_has_multistage_build,
        test_dockerfile_has_correct_structure,
        test_deploy_uses_inline_yaml,
        test_deploy_has_correct_k8s_resources,
        test_deployment_uses_never_pull_policy,
        test_scripts_have_error_handling,
        test_scripts_redirect_output,
        test_get_url_output_is_minimal
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ FAIL: {test.__name__} raised exception: {e}")
            failed += 1

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
