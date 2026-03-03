# LearnFlow - AI-Powered Python Tutoring Platform

**Adaptive Learning with AI Tutors and Teacher Safety Net**

LearnFlow is a production-ready AI-powered Python tutoring platform that provides personalized learning experiences through adaptive exercises, conversational AI tutors, and intelligent struggle detection with teacher intervention.

Built using cloud-native architecture with 7 reusable Skills for autonomous deployment.

---

## Features

- **Adaptive Exercises**: Dynamically generated Python exercises that adapt difficulty based on student performance
- **AI Chat Tutoring**: Conversational AI tutors for concepts, debugging, and code review
- **Code Execution Sandbox**: Secure Python code execution with validation and feedback
- **Progress Tracking**: Real-time mastery tracking across 8 Python modules
- **Struggle Detection**: Automatic detection of student struggles with configurable thresholds
- **Teacher Dashboard**: Real-time alerts and comprehensive student context for intervention
- **Session Monitoring**: Privacy-compliant monitoring with user consent
- **Distributed Tracing**: Full observability with OpenTelemetry across frontend and backend

---

## Quick Start

### Prerequisites

- Kubernetes cluster (Minikube, GKE, EKS, or AKS)
- kubectl configured and connected to cluster
- Helm 3.x installed
- Docker installed and running
- Python 3.9+ with pip
- Node.js 18+ with npm

### One-Command Deployment

Deploy the entire LearnFlow stack with a single command:

```bash
bash infrastructure/deploy.sh
```

This orchestrates all skills to deploy:
1. Infrastructure (Kafka, PostgreSQL)
2. Backend Services (chat, code, exercise, teacher)
3. Frontend (Next.js application)

Verify deployment:

```bash
bash infrastructure/verify-deployment.sh
```

Get the frontend URL:

```bash
kubectl get svc -n learnflow learnflow-frontend
```

For detailed deployment instructions, see [quickstart.md](specs/1-learnflow-components/quickstart.md).

---

## Architecture

### System Overview

```
┌─────────────────────────────────────────┐
│           Frontend (Next.js)            │
│  - Student Interface                    │
│  - Teacher Dashboard                    │
│  - Code Editor (Monaco)                 │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Kong API Gateway                │
│  - JWT Authentication                   │
│  - Rate Limiting                        │
│  - Request Routing                      │
└─────────────────┬───────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│ Backend        │  │ Infrastructure  │
│ Services       │  │                 │
│ - Chat         │  │ - Kafka         │
│ - Code         │  │ - PostgreSQL    │
│ - Exercise     │  │ - Dapr          │
│ - Teacher      │  │ - OpenTelemetry │
└────────────────┘  └─────────────────┘
```

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Monaco Editor
- Better Auth (JWT)
- OpenTelemetry Web SDK

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM
- OpenAI SDK (exercise generation)
- Dapr (pub/sub, state management)
- OpenTelemetry Python SDK

**Infrastructure:**
- Kubernetes (orchestration)
- Kafka (event streaming)
- PostgreSQL (database)
- Kong (API gateway)
- Helm (package management)

---

## User Stories

### 1. Student Chats with AI Tutor
Students interact with specialized AI agents for concepts, debugging, and code review through a conversational interface.

### 2. Student Runs Code in Sandbox
Students write and execute Python code in a secure sandbox with validation, test results, and feedback.

### 3. Student Practices with Adaptive Exercises
Students receive dynamically generated exercises that adapt difficulty based on performance, with progressive hints.

### 4. Teacher Intervenes When AI Can't Help
Teachers receive real-time alerts when students struggle, with comprehensive context for informed intervention.

### 5. Developer Deploys LearnFlow Using Skills
Developers deploy the entire stack autonomously using reusable skills with zero manual kubectl commands.

---

## What Are Skills?

Skills are reusable, agent-executable modules that follow this pattern:

```
SKILL.md         → Minimal instructions (~100 tokens, always loaded)
REFERENCE.md     → Deep documentation (loaded on demand)
scripts/         → Executable logic (bash/python, never loaded into context)
```

**The Golden Rule**: Scripts do the work, not the agent. All kubectl/API calls are wrapped in scripts that return minimal output (under 50 tokens), preventing token bloat and context pollution.

---

## The 7 Skills

| # | Skill | Description |
|---|---|---|
| 1 | **agents-md-gen** | Scans repo and auto-generates AGENTS.md for cross-agent compatibility |
| 2 | **kafka-k8s-setup** | Deploys Kafka on Kubernetes via Helm and creates LearnFlow topics |
| 3 | **postgres-k8s-setup** | Deploys PostgreSQL on Kubernetes and runs database migrations |
| 4 | **fastapi-dapr-agent** | Scaffolds FastAPI + Dapr microservice with K8s deployment |
| 5 | **mcp-code-execution** | Template pattern for wrapping MCP/kubectl/API calls in scripts |
| 6 | **nextjs-k8s-deploy** | Builds and deploys Next.js frontend to Kubernetes |
| 7 | **docusaurus-deploy** | Scaffolds and deploys Docusaurus documentation site |

---

## Quick Start

### Prerequisites
- Kubernetes (Minikube)
- Helm 3.x
- Docker
- kubectl
- Python 3.x
- Node.js 18+ (for frontend/docs skills)

### Using a Skill

**Via AI Agent (Claude Code, Goose):**
```
> Use the kafka-k8s-setup skill to deploy Kafka
```

**Manually:**
```bash
# Deploy Kafka
bash .claude/skills/kafka-k8s-setup/scripts/deploy.sh
python .claude/skills/kafka-k8s-setup/scripts/verify.py
bash .claude/skills/kafka-k8s-setup/scripts/create_topics.sh
```

---

## Manual Deployment (Step-by-Step)

If you prefer to deploy components individually:

### 1. Deploy Infrastructure

```bash
# Deploy Kafka
cd .claude/skills/kafka-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py
bash scripts/create_topics.sh

# Deploy PostgreSQL
cd ../postgres-k8s-setup
bash scripts/deploy.sh
python scripts/verify.py
bash scripts/migrate.sh
```

### 2. Deploy Backend Services

```bash
cd ../fastapi-dapr-agent

# Chat service
python scripts/scaffold.py chat-service backend/src/api/chat.py
bash scripts/deploy.sh chat-service
python scripts/verify.py chat-service

# Code execution service
python scripts/scaffold.py code-service backend/src/api/code.py
bash scripts/deploy.sh code-service
python scripts/verify.py code-service

# Exercise service
python scripts/scaffold.py exercise-service backend/src/api/exercises.py
bash scripts/deploy.sh exercise-service
python scripts/verify.py exercise-service

# Teacher service
python scripts/scaffold.py teacher-service backend/src/api/teacher.py
bash scripts/deploy.sh teacher-service
python scripts/verify.py teacher-service
```

### 3. Deploy Frontend

```bash
cd ../nextjs-k8s-deploy
bash scripts/build.sh ../../frontend
bash scripts/load_image.sh
bash scripts/deploy.sh
python scripts/get_url.py
```

---

## Configuration

### Environment Variables

**Backend Services:**
```bash
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/learnflow

# OpenAI (for exercise generation)
OPENAI_API_KEY=your-openai-api-key

# JWT Authentication
JWT_SECRET=your-secret-key-change-in-production

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
```

**Frontend:**
```bash
# API Gateway
NEXT_PUBLIC_KONG_URL=http://kong-gateway:8000

# Authentication
NEXT_PUBLIC_AUTH_URL=http://auth-service:8000
BETTER_AUTH_SECRET=your-auth-secret

# OpenTelemetry
NEXT_PUBLIC_OTEL_EXPORTER_URL=http://otel-collector:4318/v1/traces
```

### Kubernetes Resources

Default resource allocations:

- **Kafka**: 2 CPU, 4Gi memory
- **PostgreSQL**: 1 CPU, 2Gi memory
- **Backend Services**: 500m CPU, 512Mi memory each
- **Frontend**: 500m CPU, 512Mi memory

Adjust in Helm values or deployment manifests as needed.

---

## API Documentation

Once deployed, access API documentation at:

- **Swagger UI**: `http://<kong-url>/docs`
- **ReDoc**: `http://<kong-url>/redoc`

### Key Endpoints

**Chat:**
- `POST /api/chat/message` - Send message to AI tutor
- `GET /api/chat/history` - Get chat history

**Code:**
- `POST /api/code/execute` - Execute Python code in sandbox
- `POST /api/code/submit` - Submit code for review

**Exercises:**
- `POST /api/exercises/generate` - Generate personalized exercise
- `POST /api/exercises/submit` - Submit exercise solution
- `GET /api/exercises/hints` - Get progressive hints

**Teacher:**
- `GET /api/teacher/alerts` - Get pending struggle alerts
- `GET /api/teacher/student/:id/context` - Get student context
- `POST /api/teacher/message` - Send message to student
- `GET /api/teacher/metrics` - Get dashboard metrics

**Authentication:**
- All endpoints require `Authorization: Bearer <jwt-token>` header
- Teacher endpoints require `role: teacher` in JWT payload

---

## The MCP Code Execution Pattern

### The Problem
Direct MCP/kubectl calls flood agent context with raw JSON (10,000+ tokens), causing:
- Token waste
- Slower responses
- Context limit issues

### The Solution
Wrap all operations in scripts that filter output:

**❌ Bad (Direct Call):**
```bash
kubectl get pods -n kafka -o json
# Returns 10,000+ tokens of JSON
```

**✅ Good (Script Wrapper):**
```bash
python scripts/verify.py kafka
# Returns: ✓ 3 Kafka pods running (5 tokens)
```

**Token savings: 99.95%**

---

## Architecture

### Kubernetes Namespaces
- `kafka` - Kafka broker + Zookeeper
- `postgres` - PostgreSQL instance
- `learnflow` - All LearnFlow app services
- `dapr-system` - Dapr control plane

### Kafka Topics (LearnFlow)
- `learning.events` - General learning activity
- `code.submissions` - Student code runs
- `exercise.completions` - Finished exercises
- `struggle.alerts` - Triggers teacher notifications

### Database Schema (LearnFlow)
- `users` - User accounts and roles
- `progress` - Learning progress tracking
- `submissions` - Code submission history

---

## Adding a New Skill

1. Create skill directory:
```bash
mkdir -p .claude/skills/my-skill/scripts
```

2. Create `SKILL.md` (under 100 tokens):
```markdown
---
name: my-skill
description: One line description
tags: [tag1, tag2]
---

# my-skill

## When to Use
- Trigger condition

## Instructions
1. Run: `bash .claude/skills/my-skill/scripts/deploy.sh`

## Validation
- [ ] Check something

See [REFERENCE.md](./REFERENCE.md) for details.
```

3. Create `REFERENCE.md` with detailed documentation

4. Create scripts in `scripts/` folder:
```bash
#!/bin/bash
set -e
# Do the work...
echo "✓ Task completed"  # Minimal output only
```

5. Test manually before committing

---

## Tech Stack

- **Kubernetes (Minikube)** - Container orchestration
- **Helm** - K8s package manager
- **Kafka (Bitnami)** - Event streaming
- **PostgreSQL (Bitnami)** - Database
- **Dapr** - Microservice runtime
- **FastAPI** - Python backend framework
- **Next.js** - React frontend framework
- **Docusaurus** - Documentation site

---

## Troubleshooting

### Deployment Issues

**Pods not starting:**
```bash
kubectl get pods -n learnflow
kubectl describe pod <pod-name> -n learnflow
kubectl logs <pod-name> -n learnflow
```

**Service not accessible:**
```bash
kubectl get svc -n learnflow
kubectl port-forward svc/<service-name> 8080:80 -n learnflow
```

**Database connection errors:**
```bash
# Check PostgreSQL is running
kubectl get pods -n postgres

# Test connection
kubectl exec -it <postgres-pod> -n postgres -- psql -U postgres -d learnflow
```

**Kafka connection errors:**
```bash
# Check Kafka is running
kubectl get pods -n kafka

# List topics
kubectl exec -it <kafka-pod> -n kafka -- kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Minikube Issues

```bash
# Restart Minikube with sufficient resources
minikube delete
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Helm Issues

```bash
# Update Helm repositories
helm repo update

# Check chart versions
helm search repo bitnami/kafka --versions
helm search repo bitnami/postgresql --versions

# Debug Helm release
helm list -n <namespace>
helm status <release-name> -n <namespace>
```

### Authentication Issues

**JWT token invalid:**
- Check `JWT_SECRET` matches between auth service and API services
- Verify token hasn't expired (default: 24 hours)
- Ensure `Authorization: Bearer <token>` header is set

**Better Auth not working:**
- Check `BETTER_AUTH_SECRET` is set in frontend environment
- Verify `NEXT_PUBLIC_AUTH_URL` points to correct auth service
- Check browser console for CORS errors

### Performance Issues

**Slow API responses:**
- Check OpenTelemetry traces for bottlenecks
- Verify database connection pool settings
- Check Kafka consumer lag

**High memory usage:**
- Reduce resource limits in deployment manifests
- Check for memory leaks in application logs
- Scale down replicas if needed

---

## Development

### Local Development Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start service
uvicorn src.api.chat:app --reload --port 8001
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Running Tests

**Backend:**
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

**Frontend:**
```bash
cd frontend
npm test
npm test -- --coverage
```

### Code Quality

**Backend:**
```bash
# Linting
flake8 src/
black src/ --check
mypy src/

# Format
black src/
isort src/
```

**Frontend:**
```bash
# Linting
npm run lint

# Format
npm run format
```

---

## Monitoring and Observability

### OpenTelemetry Tracing

All services emit traces to OpenTelemetry collector:

```bash
# View traces in Jaeger UI
kubectl port-forward svc/jaeger-query 16686:16686 -n observability
# Open http://localhost:16686
```

### Metrics

Prometheus metrics available at:
- Backend services: `http://<service>:8000/metrics`
- Frontend: Web Vitals exported to OpenTelemetry

### Logging

Structured JSON logs with correlation IDs:

```bash
# View logs
kubectl logs -f <pod-name> -n learnflow

# Search logs
kubectl logs <pod-name> -n learnflow | grep "trace_id=<id>"
```

---

## Security

### Authentication

- JWT tokens with 24-hour expiration
- Role-based access control (student, teacher)
- Session monitoring requires user consent

### Data Privacy

- Data encrypted at rest and in transit
- Automatic deletion after 1 year
- User-initiated deletion available
- GDPR-compliant consent management

### Code Execution Sandbox

- Isolated Python environment
- 5-second timeout per execution
- 256MB memory limit
- No network access
- No file system access

### API Security

- Rate limiting via Kong (100 req/min students, 200 req/min teachers)
- CORS configured for frontend origin only
- Input validation on all endpoints
- SQL injection prevention via ORM

---

## Commit Message Format

All commits reflect the agentic workflow:

```
Claude: implemented User Story 3 adaptive exercises (T064-T082)
Claude: completed authentication system (T020-T022)
Claude: added error boundaries and telemetry (T121, T024)
Claude: updated README with complete setup instructions (T115)
```

---

## Project Structure

```
learnflow-skill-library/
├── README.md                           # This file
├── CLAUDE.md                           # Instructions for Claude Code
├── AGENTS.md                           # Cross-agent context
├── PHASE_2_8_STATUS.md                # Implementation status
│
├── backend/                            # Backend services
│   ├── src/
│   │   ├── api/                       # API endpoints
│   │   │   ├── chat.py                # Chat service
│   │   │   ├── code.py                # Code execution service
│   │   │   ├── exercises.py           # Exercise service
│   │   │   ├── teacher.py             # Teacher service
│   │   │   ├── docs.py                # API documentation
│   │   │   └── middleware/
│   │   │       └── auth.py            # JWT authentication
│   │   ├── models/                    # SQLAlchemy models
│   │   │   ├── student.py
│   │   │   ├── session.py
│   │   │   ├── message.py
│   │   │   ├── exercise.py
│   │   │   ├── struggle_event.py
│   │   │   └── teacher_alert.py
│   │   ├── services/                  # Business logic
│   │   │   ├── difficulty_service.py
│   │   │   ├── struggle_detection_service.py
│   │   │   └── alert_service.py
│   │   ├── agents/                    # AI agents
│   │   │   └── exercise_generator.py
│   │   ├── events/                    # Kafka events
│   │   └── observability/             # OpenTelemetry
│   └── requirements.txt
│
├── frontend/                           # Next.js frontend
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── login/
│   │   │   ├── student/
│   │   │   └── teacher/
│   │   ├── components/                # React components
│   │   │   ├── Chat/
│   │   │   ├── CodeEditor/
│   │   │   ├── Exercise/
│   │   │   ├── Teacher/
│   │   │   ├── ConsentDialog.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── lib/                       # Utilities
│   │   │   ├── auth.ts                # Better Auth client
│   │   │   └── telemetry.ts           # OpenTelemetry
│   │   └── services/                  # API clients
│   └── package.json
│
├── infrastructure/                     # Deployment scripts
│   ├── deploy.sh                      # One-command deployment
│   ├── verify-deployment.sh           # Verification script
│   ├── dapr/                          # Dapr components
│   ├── helm/                          # Helm values
│   └── k8s/                           # Kubernetes manifests
│
├── specs/                             # Specifications
│   └── 1-learnflow-components/
│       ├── spec.md                    # Feature requirements
│       ├── plan.md                    # Architecture decisions
│       ├── tasks.md                   # Task breakdown
│       └── quickstart.md              # Deployment guide
│
├── history/                           # Prompt History Records
│   ├── prompts/
│   │   └── 1-learnflow-components/
│   └── adr/                           # Architecture Decision Records
│
└── .claude/                           # Skills library
    └── skills/
        ├── agents-md-gen/
        ├── kafka-k8s-setup/
        ├── postgres-k8s-setup/
        ├── fastapi-dapr-agent/
        ├── mcp-code-execution/
        ├── nextjs-k8s-deploy/
        └── docusaurus-deploy/
```

---

## Roadmap

### Completed ✅

- [x] User Story 1: Student chats with AI tutor
- [x] User Story 2: Student runs code in sandbox
- [x] User Story 3: Student practices with adaptive exercises
- [x] User Story 4: Teacher intervenes when AI can't help
- [x] User Story 5: Developer deploys using skills
- [x] Authentication system (Better Auth + JWT)
- [x] Error boundaries for stability
- [x] Frontend OpenTelemetry tracing
- [x] API documentation (OpenAPI/Swagger)
- [x] Session monitoring consent dialog

### In Progress 🚧

- [ ] Infrastructure deployment (run deploy.sh on cluster)
- [ ] Data retention and privacy policies
- [ ] Loading states across components
- [ ] CI/CD pipeline

### Planned 📋

- [ ] Accessibility improvements (ARIA labels)
- [ ] Performance optimization (bundle size, Web Vitals)
- [ ] Security scanning (Dependabot, CodeQL)
- [ ] Kong rate limiting configuration
- [ ] Full deployment validation

---

## Contributing

1. Follow the MCP Code Execution pattern for all skills
2. Keep SKILL.md under 100 tokens
3. All scripts must return minimal output (under 50 tokens)
4. Write tests for all new features
5. Use conventional commit messages
6. Update documentation for user-facing changes

### Development Workflow

1. Create feature branch from `main`
2. Implement changes with tests
3. Run linting and tests locally
4. Create Prompt History Record (PHR)
5. Commit with format: `Claude: <description>`
6. Create pull request with description

---

## License

MIT

---

## Support

For issues or questions:
- Check logs: `kubectl logs -n learnflow <pod-name>`
- Review skill documentation in `.claude/skills/`
- Verify Kubernetes cluster health
- Check [PHASE_2_8_STATUS.md](PHASE_2_8_STATUS.md) for implementation status
- See [quickstart.md](specs/1-learnflow-components/quickstart.md) for deployment help

---

**Built with ❤️ using Reusable Intelligence and Cloud-Native Architecture**
