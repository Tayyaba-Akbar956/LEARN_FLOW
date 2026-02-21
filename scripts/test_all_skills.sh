#!/bin/bash
# -*- coding: utf-8 -*-
# Master test runner for all 7 skills

set -e

echo "========================================="
echo "SKILLS LIBRARY — TEST SUITE"
echo "========================================="
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test each skill
SKILLS=(
  "agents-md-gen"
  "kafka-k8s-setup"
  "postgres-k8s-setup"
  "fastapi-dapr-agent"
  "mcp-code-execution"
  "nextjs-k8s-deploy"
  "docusaurus-deploy"
)

for i in "${!SKILLS[@]}"; do
  SKILL="${SKILLS[$i]}"
  NUM=$((i + 1))

  echo "[$NUM/7] Testing $SKILL..."

  # Run test if it exists
  if [ -f ".claude/skills/$SKILL/tests/test_skill.py" ]; then
    if python ".claude/skills/$SKILL/tests/test_skill.py"; then
      PASSED_TESTS=$((PASSED_TESTS + 1))
    else
      FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
  else
    echo "✗ SKIP: No test file found"
  fi

  echo ""
done

echo "========================================="
echo "TEST SUMMARY"
echo "========================================="
echo "Total: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: $FAILED_TESTS"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
  echo "✓ ALL TESTS PASSED"
  exit 0
else
  echo "✗ SOME TESTS FAILED"
  exit 1
fi
