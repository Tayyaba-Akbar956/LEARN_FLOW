#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real execution tests for fastapi-dapr-agent skill"""
import os
import sys
import subprocess
import shutil

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

TEST_SERVICE = 'test-service-exec'
TEST_DIR = f'services/{TEST_SERVICE}'

def cleanup_test_service():
    """Clean up test service directory"""
    if os.path.exists(TEST_DIR):
        shutil.rmtree(TEST_DIR)

def test_scaffold_script_executes():
    """Test that scaffold.py actually runs and exits 0"""
    cleanup_test_service()

    result = subprocess.run(
        ['python', '.claude/skills/fastapi-dapr-agent/scripts/scaffold.py', TEST_SERVICE],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: scaffold.py exited with code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        cleanup_test_service()
        return False

    print("✓ PASS: scaffold.py executes and exits 0")
    return True

def test_scaffold_creates_all_files():
    """Test that scaffold.py actually creates all required files"""
    required_files = ['main.py', 'requirements.txt', 'Dockerfile', 'k8s-deployment.yaml']
    missing = []

    for file in required_files:
        if not os.path.exists(f'{TEST_DIR}/{file}'):
            missing.append(file)

    if missing:
        print(f"✗ FAIL: scaffold.py did not create: {', '.join(missing)}")
        cleanup_test_service()
        return False

    print("✓ PASS: scaffold.py creates all required files")
    return True

def test_generated_main_py_is_valid():
    """Test that generated main.py is valid Python"""
    main_path = f'{TEST_DIR}/main.py'

    if not os.path.exists(main_path):
        print("✗ FAIL: main.py does not exist")
        cleanup_test_service()
        return False

    # Check Python syntax
    result = subprocess.run(
        ['python', '-m', 'py_compile', main_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: main.py has syntax errors: {result.stderr}")
        cleanup_test_service()
        return False

    # Check content
    with open(main_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_elements = ['FastAPI', '/health', '/invoke', 'uvicorn']
    missing = []

    for element in required_elements:
        if element not in content:
            missing.append(element)

    if missing:
        print(f"✗ FAIL: main.py missing elements: {', '.join(missing)}")
        cleanup_test_service()
        return False

    print("✓ PASS: Generated main.py is valid Python with required endpoints")
    return True

def test_generated_dockerfile_is_valid():
    """Test that generated Dockerfile has correct structure"""
    dockerfile_path = f'{TEST_DIR}/Dockerfile'

    if not os.path.exists(dockerfile_path):
        print("✗ FAIL: Dockerfile does not exist")
        cleanup_test_service()
        return False

    with open(dockerfile_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_elements = ['FROM python:', 'COPY requirements.txt', 'RUN pip install', 'CMD']
    missing = []

    for element in required_elements:
        if element not in content:
            missing.append(element)

    if missing:
        print(f"✗ FAIL: Dockerfile missing elements: {', '.join(missing)}")
        cleanup_test_service()
        return False

    print("✓ PASS: Generated Dockerfile has correct structure")
    return True

def test_generated_k8s_yaml_is_valid():
    """Test that generated k8s-deployment.yaml is valid YAML"""
    yaml_path = f'{TEST_DIR}/k8s-deployment.yaml'

    if not os.path.exists(yaml_path):
        print("✗ FAIL: k8s-deployment.yaml does not exist")
        cleanup_test_service()
        return False

    with open(yaml_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for required Kubernetes elements
    required_elements = [
        'apiVersion: apps/v1',
        'kind: Deployment',
        'kind: Service',
        'dapr.io/enabled: "true"',
        f'dapr.io/app-id: "{TEST_SERVICE}"',
        'imagePullPolicy: Never'
    ]
    missing = []

    for element in required_elements:
        if element not in content:
            missing.append(element)

    if missing:
        print(f"✗ FAIL: k8s-deployment.yaml missing elements: {', '.join(missing)}")
        cleanup_test_service()
        return False

    print("✓ PASS: Generated k8s-deployment.yaml is valid with Dapr annotations")
    return True

def test_scaffold_output_is_minimal():
    """Test that scaffold.py output is actually minimal"""
    cleanup_test_service()

    result = subprocess.run(
        ['python', '.claude/skills/fastapi-dapr-agent/scripts/scaffold.py', TEST_SERVICE],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    token_count = len(output.split())

    if token_count > 10:
        print(f"✗ FAIL: scaffold.py output too verbose ({token_count} tokens)")
        cleanup_test_service()
        return False

    # Check for success indicator (either checkmark or "scaffolded")
    if 'scaffolded' not in output.lower():
        print(f"✗ FAIL: scaffold.py output missing success indicator: {output}")
        cleanup_test_service()
        return False

    print(f"✓ PASS: scaffold.py output is minimal ({token_count} tokens)")
    cleanup_test_service()
    return True

def test_deploy_script_syntax():
    """Test that deploy.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/fastapi-dapr-agent/scripts/deploy.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: deploy.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: deploy.sh has valid bash syntax")
    return True

def test_verify_script_executes():
    """Test that verify.py can execute"""
    result = subprocess.run(
        ['python', '.claude/skills/fastapi-dapr-agent/scripts/verify.py', 'test-service'],
        capture_output=True, text=True
    )

    # Check that it exits with 0 or 1 (not crash)
    if result.returncode not in [0, 1]:
        print(f"✗ FAIL: verify.py crashed with exit code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    print(f"✓ PASS: verify.py executes correctly (exit {result.returncode})")
    return True

def main():
    """Run all execution tests"""
    tests = [
        test_scaffold_script_executes,
        test_scaffold_creates_all_files,
        test_generated_main_py_is_valid,
        test_generated_dockerfile_is_valid,
        test_generated_k8s_yaml_is_valid,
        test_scaffold_output_is_minimal,
        test_deploy_script_syntax,
        test_verify_script_executes
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

    # Final cleanup
    cleanup_test_service()

    return 0 if failed == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
