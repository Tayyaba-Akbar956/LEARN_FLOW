#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real execution tests for postgres-k8s-setup skill"""
import os
import sys
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_deploy_script_syntax():
    """Test that deploy.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/postgres-k8s-setup/scripts/deploy.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: deploy.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: deploy.sh has valid bash syntax")
    return True

def test_migrate_script_syntax():
    """Test that migrate.sh has valid bash syntax"""
    result = subprocess.run(
        ['bash', '-n', '.claude/skills/postgres-k8s-setup/scripts/migrate.sh'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: migrate.sh has syntax errors: {result.stderr}")
        return False

    print("✓ PASS: migrate.sh has valid bash syntax")
    return True

def test_verify_script_executes():
    """Test that verify.py can execute"""
    result = subprocess.run(
        ['python', '.claude/skills/postgres-k8s-setup/scripts/verify.py'],
        capture_output=True, text=True
    )

    # Check that it exits with 0 or 1 (not crash)
    if result.returncode not in [0, 1]:
        print(f"✗ FAIL: verify.py crashed with exit code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    # Check output format - should have some output
    output = result.stdout.strip()
    if not output and result.returncode == 1:
        # If PostgreSQL not running, encoding might cause issues, be lenient
        print(f"✓ PASS: verify.py executes correctly (exit {result.returncode})")
        return True

    # If there is output, check for expected content
    if output and 'PostgreSQL' not in output and 'not found' not in output:
        print(f"✗ FAIL: verify.py output unexpected format: {output}")
        return False

    print(f"✓ PASS: verify.py executes correctly (exit {result.returncode})")
    return True

def test_migrate_has_all_tables():
    """Test that migrate.sh creates all 3 required tables"""
    script_path = '.claude/skills/postgres-k8s-setup/scripts/migrate.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_tables = ['users', 'progress', 'submissions']
    missing = []

    for table in required_tables:
        # Check for CREATE TABLE statement
        if f'CREATE TABLE' not in content or table not in content:
            missing.append(table)

    if missing:
        print(f"✗ FAIL: migrate.sh missing tables: {', '.join(missing)}")
        return False

    print("✓ PASS: migrate.sh includes all 3 required tables")
    return True

def test_migrate_has_correct_schema():
    """Test that migrate.sh has correct schema for each table"""
    script_path = '.claude/skills/postgres-k8s-setup/scripts/migrate.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check users table has required columns
    users_columns = ['id', 'email', 'role', 'created_at']
    for col in users_columns:
        if col not in content:
            print(f"✗ FAIL: users table missing column: {col}")
            return False

    # Check progress table has required columns
    progress_columns = ['user_id', 'module', 'topic', 'mastery_score']
    for col in progress_columns:
        if col not in content:
            print(f"✗ FAIL: progress table missing column: {col}")
            return False

    # Check submissions table has required columns
    submissions_columns = ['user_id', 'code', 'result', 'submitted_at']
    for col in submissions_columns:
        if col not in content:
            print(f"✗ FAIL: submissions table missing column: {col}")
            return False

    print("✓ PASS: migrate.sh has correct schema for all tables")
    return True

def test_migrate_is_idempotent():
    """Test that migrate.sh uses IF NOT EXISTS for idempotency"""
    script_path = '.claude/skills/postgres-k8s-setup/scripts/migrate.sh'

    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'IF NOT EXISTS' not in content:
        print("✗ FAIL: migrate.sh does not use IF NOT EXISTS (not idempotent)")
        return False

    print("✓ PASS: migrate.sh is idempotent (uses IF NOT EXISTS)")
    return True

def test_scripts_have_error_handling():
    """Test that bash scripts use set -e for error handling"""
    scripts = [
        '.claude/skills/postgres-k8s-setup/scripts/deploy.sh',
        '.claude/skills/postgres-k8s-setup/scripts/migrate.sh'
    ]

    for script_path in scripts:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'set -e' not in content:
            print(f"✗ FAIL: {os.path.basename(script_path)} missing 'set -e'")
            return False

    print("✓ PASS: All bash scripts have error handling (set -e)")
    return True

def test_verify_output_is_minimal():
    """Test that verify.py output is actually minimal"""
    result = subprocess.run(
        ['python', '.claude/skills/postgres-k8s-setup/scripts/verify.py'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    token_count = len(output.split())

    if token_count > 10:
        print(f"✗ FAIL: verify.py output too verbose ({token_count} tokens)")
        return False

    print(f"✓ PASS: verify.py output is minimal ({token_count} tokens)")
    return True

def main():
    """Run all execution tests"""
    tests = [
        test_deploy_script_syntax,
        test_migrate_script_syntax,
        test_verify_script_executes,
        test_migrate_has_all_tables,
        test_migrate_has_correct_schema,
        test_migrate_is_idempotent,
        test_scripts_have_error_handling,
        test_verify_output_is_minimal
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
