#!/bin/bash
# LearnFlow Deployment Verification Script
# Verifies all services are running correctly

set -e

echo "🔍 Verifying LearnFlow Deployment..."
echo ""

NAMESPACE="learnflow"
FAILED=0

# Function to check pod status in a specific namespace
check_pod() {
    local name=$1
    local ns=$2
    echo -n "  Checking $name in namespace $ns... "

    local pod_list=$(kubectl get pods -n $ns -l app.kubernetes.io/name=$name -o jsonpath='{.items}')
    if [[ "$pod_list" == "[]" ]]; then
        # Fallback to app labels if app.kubernetes.io/name fails
        pod_list=$(kubectl get pods -n $ns -l app=$name -o jsonpath='{.items}')
    fi

    if [[ "$pod_list" != "[]" ]]; then
        local status=$(kubectl get pods -n $ns -l app.kubernetes.io/name=$name -o jsonpath='{.items[0].status.phase}' 2>/dev/null || kubectl get pods -n $ns -l app=$name -o jsonpath='{.items[0].status.phase}' 2>/dev/null)
        if [ "$status" == "Running" ]; then
            echo "✅ Running"
        else
            echo "❌ Status: $status"
            FAILED=1
        fi
    else
        echo "❌ Not found"
        FAILED=1
    fi
}

# Function to check service in a specific namespace
check_service() {
    local name=$1
    local ns=$2
    echo -n "  Checking $name service in namespace $ns... "

    if kubectl get svc -n $ns $name &> /dev/null; then
        echo "✅ Exists"
    else
        echo "❌ Not found"
        FAILED=1
    fi
}

echo "📦 Infrastructure:"
check_pod "kafka" "kafka"
check_pod "postgresql" "postgres"
echo ""

echo "🔧 Backend Services:"
check_pod "chat-service" "$NAMESPACE"
check_pod "code-service" "$NAMESPACE"
check_pod "exercise-service" "$NAMESPACE"
check_pod "teacher-service" "$NAMESPACE"
echo ""

echo "🎨 Frontend:"
check_pod "learnflow-frontend" "$NAMESPACE"
echo ""

echo "🌐 Services:"
check_service "kafka" "kafka"
check_service "postgresql" "postgres"
check_service "chat-service" "$NAMESPACE"
check_service "code-service" "$NAMESPACE"
check_service "exercise-service" "$NAMESPACE"
check_service "teacher-service" "$NAMESPACE"
check_service "learnflow-frontend" "$NAMESPACE"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All services verified successfully!"
    echo ""
    echo "🌐 Frontend URL:"
    kubectl get svc -n $NAMESPACE learnflow-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
    echo ""
    exit 0
else
    echo "❌ Some services failed verification"
    echo ""
    echo "📋 Debug commands:"
    echo "  kubectl get pods -n $NAMESPACE"
    echo "  kubectl logs -n $NAMESPACE <pod-name>"
    echo "  kubectl describe pod -n $NAMESPACE <pod-name>"
    exit 1
fi
