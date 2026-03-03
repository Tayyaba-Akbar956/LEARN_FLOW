#!/bin/bash
# Test runner for all LearnFlow services
# Runs each service test individually to avoid pytest import conflicts

set -e

SERVICES=(
    "code-review-agent"
    "concepts-agent"
    "debug-agent"
    "exercise-agent"
    "progress-agent"
    "triage-agent"
)

echo "Running all LearnFlow service tests..."
echo "======================================"

TOTAL_PASSED=0
TOTAL_FAILED=0

for service in "${SERVICES[@]}"; do
    echo ""
    echo "Testing $service..."
    if pytest "services/$service/test_main.py" -v --tb=short; then
        echo "✓ $service tests passed"
    else
        echo "✗ $service tests failed"
        TOTAL_FAILED=$((TOTAL_FAILED + 1))
    fi
    TOTAL_PASSED=$((TOTAL_PASSED + 1))
done

echo ""
echo "======================================"
echo "Test Summary:"
echo "Services tested: ${#SERVICES[@]}"
echo "All tests passed: $((${#SERVICES[@]} - TOTAL_FAILED))"
echo "Failed: $TOTAL_FAILED"

if [ $TOTAL_FAILED -eq 0 ]; then
    echo "✓ ALL TESTS PASSED"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    exit 1
fi
