#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Real execution tests for mcp-code-execution skill"""
import os
import sys
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_mcp_client_executes():
    """Test that mcp_client.py actually runs"""
    result = subprocess.run(
        ['python', '.claude/skills/mcp-code-execution/scripts/mcp_client.py', 'default'],
        capture_output=True, text=True
    )

    # Should exit with 0 or 1 (not crash)
    if result.returncode not in [0, 1]:
        print(f"✗ FAIL: mcp_client.py crashed with exit code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    print(f"✓ PASS: mcp_client.py executes correctly (exit {result.returncode})")
    return True

def test_mcp_client_output_is_minimal():
    """Test that mcp_client.py output is actually minimal"""
    result = subprocess.run(
        ['python', '.claude/skills/mcp-code-execution/scripts/mcp_client.py', 'default'],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    lines = output.split('\n')

    # Should be minimal - one line per pod or error message
    if len(lines) > 20:
        print(f"✗ FAIL: mcp_client.py output too verbose ({len(lines)} lines)")
        return False

    # Check that it uses the minimal format
    if output and '✓' not in output and '✗' not in output:
        print(f"✗ FAIL: mcp_client.py output missing status indicators")
        return False

    print(f"✓ PASS: mcp_client.py output is minimal ({len(lines)} lines)")
    return True

def test_create_wrapper_executes():
    """Test that create_mcp_wrapper.py actually runs and creates file"""
    test_tool = 'test_wrapper_exec'

    # Change to skill directory
    original_dir = os.getcwd()
    skill_dir = '.claude/skills/mcp-code-execution'
    os.chdir(skill_dir)

    wrapper_path = f'scripts/{test_tool}_wrapper.py'

    # Clean up if exists
    if os.path.exists(wrapper_path):
        os.remove(wrapper_path)

    # Run create_mcp_wrapper
    result = subprocess.run(
        ['python', 'scripts/create_mcp_wrapper.py', test_tool],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        os.chdir(original_dir)
        print(f"✗ FAIL: create_mcp_wrapper.py exited with code {result.returncode}")
        print(f"  stderr: {result.stderr}")
        return False

    if not os.path.exists(wrapper_path):
        os.chdir(original_dir)
        print("✗ FAIL: create_mcp_wrapper.py did not create wrapper file")
        return False

    # Clean up
    os.remove(wrapper_path)
    os.chdir(original_dir)
    print("✓ PASS: create_mcp_wrapper.py executes and creates wrapper file")
    return True

def test_generated_wrapper_is_valid_python():
    """Test that generated wrapper is valid Python"""
    test_tool = 'test_wrapper_valid'

    # Change to skill directory
    original_dir = os.getcwd()
    skill_dir = '.claude/skills/mcp-code-execution'
    os.chdir(skill_dir)

    wrapper_path = f'scripts/{test_tool}_wrapper.py'

    # Generate wrapper
    subprocess.run(
        ['python', 'scripts/create_mcp_wrapper.py', test_tool],
        capture_output=True, text=True
    )

    if not os.path.exists(wrapper_path):
        os.chdir(original_dir)
        print("✗ FAIL: Wrapper file not created")
        return False

    # Check Python syntax
    result = subprocess.run(
        ['python', '-m', 'py_compile', wrapper_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        os.remove(wrapper_path)
        os.chdir(original_dir)
        print(f"✗ FAIL: Generated wrapper has syntax errors: {result.stderr}")
        return False

    # Clean up
    os.remove(wrapper_path)
    os.chdir(original_dir)
    print("✓ PASS: Generated wrapper is valid Python")
    return True

def test_generated_wrapper_has_pattern_docs():
    """Test that generated wrapper includes MCP pattern documentation"""
    test_tool = 'test_wrapper_docs'

    # Change to skill directory
    original_dir = os.getcwd()
    skill_dir = '.claude/skills/mcp-code-execution'
    os.chdir(skill_dir)

    wrapper_path = f'scripts/{test_tool}_wrapper.py'

    # Generate wrapper
    subprocess.run(
        ['python', 'scripts/create_mcp_wrapper.py', test_tool],
        capture_output=True, text=True
    )

    if not os.path.exists(wrapper_path):
        os.chdir(original_dir)
        print("✗ FAIL: Wrapper file not created")
        return False

    with open(wrapper_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_elements = [
        'MCP Code Execution Pattern',
        'GOLDEN RULE',
        'Never return raw API responses',
        'Always filter to essential information',
        'Keep output under 50 tokens'
    ]

    missing = []
    for element in required_elements:
        if element not in content:
            missing.append(element)

    # Clean up
    os.remove(wrapper_path)
    os.chdir(original_dir)

    if missing:
        print(f"✗ FAIL: Generated wrapper missing documentation: {', '.join(missing)}")
        return False

    print("✓ PASS: Generated wrapper includes MCP pattern documentation")
    return True

def test_create_wrapper_output_is_minimal():
    """Test that create_mcp_wrapper.py output is minimal"""
    test_tool = 'test_wrapper_output'

    # Change to skill directory
    original_dir = os.getcwd()
    skill_dir = '.claude/skills/mcp-code-execution'
    os.chdir(skill_dir)

    wrapper_path = f'scripts/{test_tool}_wrapper.py'

    result = subprocess.run(
        ['python', 'scripts/create_mcp_wrapper.py', test_tool],
        capture_output=True, text=True
    )

    output = result.stdout.strip()
    token_count = len(output.split())

    # Clean up
    if os.path.exists(wrapper_path):
        os.remove(wrapper_path)
    os.chdir(original_dir)

    if token_count > 10:
        print(f"✗ FAIL: create_mcp_wrapper.py output too verbose ({token_count} tokens)")
        return False

    # Check for success indicator (either checkmark or "Created")
    if 'Created' not in output and 'created' not in output:
        print(f"✗ FAIL: create_mcp_wrapper.py output missing success indicator: {output}")
        return False

    print(f"✓ PASS: create_mcp_wrapper.py output is minimal ({token_count} tokens)")
    return True

def test_reference_has_token_comparison():
    """Test that REFERENCE.md actually includes token comparison"""
    ref_path = '.claude/skills/mcp-code-execution/REFERENCE.md'

    if not os.path.exists(ref_path):
        print("✗ FAIL: REFERENCE.md does not exist")
        return False

    with open(ref_path, 'r', encoding='utf-8') as f:
        content = f.read()

    required_sections = [
        'Token Comparison',
        'Direct MCP',
        'Skills + Scripts',
        '99.95%'  # Token savings percentage
    ]

    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)

    if missing:
        print(f"✗ FAIL: REFERENCE.md missing: {', '.join(missing)}")
        return False

    print("✓ PASS: REFERENCE.md includes complete token comparison")
    return True

def main():
    """Run all execution tests"""
    tests = [
        test_mcp_client_executes,
        test_mcp_client_output_is_minimal,
        test_create_wrapper_executes,
        test_generated_wrapper_is_valid_python,
        test_generated_wrapper_has_pattern_docs,
        test_create_wrapper_output_is_minimal,
        test_reference_has_token_comparison
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
