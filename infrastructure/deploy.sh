#!/bin/bash
# LearnFlow Deployment Script
# Orchestrates all skills to deploy the complete LearnFlow stack

set -e

echo "🚀 Starting LearnFlow deployment..."
echo ""

# Check if we're in the right directory
if [ ! -d ".claude/skills" ]; then
    echo "❌ Error: Must run from repository root"
    exit 1
fi

# Phase 1: Deploy Infrastructure
echo "📦 Phase 1: Deploying Infrastructure..."
echo ""

# Deploy Kafka
echo "  → Deploying Kafka..."
cd .claude/skills/kafka-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py
cd ../../..

# Deploy PostgreSQL
echo "  → Deploying PostgreSQL..."
cd .claude/skills/postgres-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py
cd ../../..

echo "✅ Infrastructure deployed successfully"
echo ""

# Phase 2: Deploy Backend Services
echo "🔧 Phase 2: Deploying Backend Services..."
echo ""

# Deploy chat service
echo "  → Deploying chat service..."
cd .claude/skills/fastapi-dapr-agent
python scripts/scaffold.py chat-service backend/src/api/chat.py
bash scripts/deploy.sh chat-service
python scripts/verify.py chat-service
cd ../../..

# Deploy code execution service
echo "  → Deploying code execution service..."
cd .claude/skills/fastapi-dapr-agent
python scripts/scaffold.py code-service backend/src/api/code.py
bash scripts/deploy.sh code-service
python scripts/verify.py code-service
cd ../../..

# Deploy exercise service
echo "  → Deploying exercise service..."
cd .claude/skills/fastapi-dapr-agent
python scripts/scaffold.py exercise-service backend/src/api/exercises.py
bash scripts/deploy.sh exercise-service
python scripts/verify.py exercise-service
cd ../../..

# Deploy teacher service
echo "  → Deploying teacher service..."
cd .claude/skills/fastapi-dapr-agent
python scripts/scaffold.py teacher-service backend/src/api/teacher.py
bash scripts/deploy.sh teacher-service
python scripts/verify.py teacher-service
cd ../../..

echo "✅ Backend services deployed successfully"
echo ""

# Phase 3: Deploy Frontend
echo "🎨 Phase 3: Deploying Frontend..."
echo ""

cd .claude/skills/nextjs-k8s-deploy
bash scripts/build.sh ../../frontend
bash scripts/load_image.sh
bash scripts/deploy.sh
python scripts/get_url.py
cd ../../..

echo "✅ Frontend deployed successfully"
echo ""

# Phase 4: Verify Deployment
echo "🔍 Phase 4: Verifying Deployment..."
echo ""

bash infrastructure/verify-deployment.sh

echo ""
echo "✅ LearnFlow deployment complete!"
echo ""
echo "📊 Deployment Summary:"
echo "  - Infrastructure: Kafka, PostgreSQL"
echo "  - Backend Services: chat, code, exercise, teacher"
echo "  - Frontend: Next.js application"
echo ""
echo "🌐 Access your deployment:"
echo "  Run: kubectl get svc -n learnflow"
echo ""
