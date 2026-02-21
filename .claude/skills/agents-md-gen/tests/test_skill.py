#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real execution tests for agents-md-gen skill"""
import os
import sys
import subprocess
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_scan_repo_executes():
    """Test that scan_repo.py actually runs and exits 0"""
    result = subprocess.run(
        ['python', '.claude/skills/agents-md-gen/scripts/scan_repo.py'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: scan_repo.py exited with code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    print("✓ PASS: scan_repo.py executes and exits 0")
    return True

def test_scan_repo_returns_valid_json():
    """Test that scan_repo.py returns valid JSON with required fields"""
    result = subprocess.run(
        ['python', '.claude/skills/agents-md-gen/scripts/scan_repo.py'],
        capture_output=True, text=True
    )

    try:
        data = json.loads(result.stdout)

        if 'tech_stack' not in data:
            print("✗ FAIL: scan_repo.py output missing 'tech_stack' field")
            return False

        if 'structure' not in data:
            print("✗ FAIL: scan_repo.py output missing 'structure' field")
            return False

        if not isinstance(data['tech_stack'], list):
            print("✗ FAIL: tech_stack is not a list")
            return False

        print("✓ PASS: scan_repo.py returns valid JSON with required fields")
        return True

    except json.JSONDecodeError as e:
        print(f"✗ FAIL: scan_repo.py did not return valid JSON: {e}")
        return False

def test_generate_agents_md_executes():
    """Test that generate_agents_md.py actually runs and creates AGENTS.md"""
    # Remove existing AGENTS.md
    if os.path.exists('AGENTS.md'):
        os.remove('AGENTS.md')

    result = subprocess.run(
        ['python', '.claude/skills/agents-md-gen/scripts/generate_agents_md.py'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"✗ FAIL: generate_agents_md.py exited with code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    if not os.path.exists('AGENTS.md'):
        print("✗ FAIL: generate_agents_md.py did not create AGENTS.md")
        return False

    print("✓ PASS: generate_agents_md.py executes and creates AGENTS.md")
    return True

def test_agents_md_has_required_content():
    """Test that generated AGENTS.md actually contains required sections"""
    if not os.path.exists('AGENTS.md'):
        print("✗ FAIL: AGENTS.md does not exist")
        return False

    with open('AGENTS.md', 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        '# AGENTS.md',
        'Project Overview',
        'Tech Stack',
        'Project Structure',
        'Agent Instructions',
        'Available Skills'
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"✗ FAIL: AGENTS.md missing sections: {', '.join(missing)}")
        return False

    # Check that it lists the 7 skills
    skills = ['agents-md-gen', 'kafka-k8s-setup', 'postgres-k8s-setup',
              'fastapi-dapr-agent', 'mcp-code-execution', 'nextjs-k8s-deploy',
              'docusaurus-deploy']

    found_skills = sum(1 for skill in skills if skill in content)

    if found_skills < 7:
        print(f"✗ FAIL: AGENTS.md only mentions {found_skills}/7 skills")
        return False

    print("✓ PASS: AGENTS.md contains all required sections and skills")
    return True

def test_output_is_minimal():
    """Test that generate_agents_md.py output is actually minimal"""
    result = subprocess.run(
        ['python', '.claude/skills/agents-md-gen/scripts/generate_agents_md.py'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    token_count = len(output.split())

    if token_count > 10:
        print(f"✗ FAIL: Output too verbose ({token_count} tokens): {output}")
        return False

    # Check for success indicator (either ✓ or the word "generated")
    if 'generated' not in output.lower():
        print(f"✗ FAIL: Output missing success indicator: {output}")
        return False

    print(f"✓ PASS: Output is minimal ({token_count} tokens)")
    return True

def main():
    """Run all execution tests"""
    tests = [
        test_scan_repo_executes,
        test_scan_repo_returns_valid_json,
        test_generate_agents_md_executes,
        test_agents_md_has_required_content,
        test_output_is_minimal
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
