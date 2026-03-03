# Implementation Plan: LearnFlow Core Components

**Branch**: `1-learnflow-components` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-learnflow-components/spec.md`

## Summary

LearnFlow is an AI-powered Python tutoring platform that proves three things: (1) AI agents can teach humans through adaptive, discovery-based tutoring, (2) AI agents can build software autonomously using Claude Code and Goose, and (3) reusable skills are the future of software development. The platform consists of 6 core components: Chat Interface with multi-agent routing, Code Editor with sandboxed execution, Exercise System with adaptive difficulty, Struggle Detection for proactive intervention, Teacher Dashboard for human oversight, and Skills Library for autonomous infrastructure deployment.

**Technical Approach**: Microservices architecture on Kubernetes with event-driven communication via Kafka, FastAPI backends orchestrated by Dapr, Next.js frontend with Monaco Editor, OpenAI Agent SDK with Groq models for tutoring, and comprehensive observability via OpenTelemetry. All infrastructure deployed using reusable skills following the MCP Code Execution pattern.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend), Bash (skills scripts)
**Primary Dependencies**: FastAPI, Next.js 14, OpenAI Agent SDK, Dapr, Kafka, PostgreSQL, Monaco Editor
**Storage**: PostgreSQL 15 (student data, sessions, progress), Kafka (event streaming)
**Testing**: pytest (backend), Jest + React Testing Library (frontend), contract tests (OpenAPI validation)
**Target Platform**: Kubernetes (Minikube for dev, cloud-agnostic for production)
**Project Type**: Web application (frontend + backend microservices)
**Performance Goals**: <3s chat response, <5s code execution, <2s exercise generation, <30s teacher alert delivery
**Constraints**: <50 tokens per MCP script output, 256MB sandbox memory limit, 5s code execution timeout, 1 year data retention
**Scale/Scope**: 100 concurrent students (MVP), 10k exercises generated/day, 95% infrastructure via skills, <10% teacher intervention rate

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Article I: Skills First ✅ PASS
- **Requirement**: All infrastructure MUST use skills
- **Status**: COMPLIANT - kafka-k8s-setup, postgres-k8s-setup, fastapi-dapr-agent, nextjs-k8s-deploy skills exist
- **Verification**: FR-036 requires "All LearnFlow infrastructure MUST be deployable using skills"

### Article II: Tests Before Code (Strict TDD) ✅ PASS
- **Requirement**: Red-green-refactor cycle enforced via commit history
- **Status**: COMPLIANT - Will be enforced during implementation phase
- **Verification**: Git hooks will validate commit message format and sequence

### Article III: Minimal Context (MCP Code Execution) ✅ PASS
- **Requirement**: All external calls wrapped in scripts returning <50 tokens
- **Status**: COMPLIANT - FR-034 requires MCP pattern, existing skills demonstrate compliance
- **Verification**: All verification scripts in skills return under 50 tokens

### Article IV: Agents Build, Humans Teach ✅ PASS
- **Requirement**: AI agents write code, humans write specs
- **Status**: COMPLIANT - This plan written by Claude Code, implementation will follow
- **Verification**: Commit messages will indicate agent authorship

### Article V: Real Behavior Over Fake Demos ✅ PASS
- **Requirement**: No hardcoded responses, real data only
- **Status**: COMPLIANT - FR-008 to FR-012 require real agent routing and responses
- **Verification**: Integration tests will validate real data flows

### Article VI: Adaptive Learning ✅ PASS
- **Requirement**: Real-time struggle detection and escalation
- **Status**: COMPLIANT - FR-024 to FR-029 define struggle detection system
- **Verification**: SC-007 requires detection within 2 minutes of threshold

### Article VII: Autonomy Is The Metric ✅ PASS
- **Requirement**: Minimize human intervention
- **Status**: COMPLIANT - SC-011 requires <5 clarifying questions for full deployment
- **Verification**: SC-014 requires <10% teacher intervention rate

**GATE RESULT**: ✅ ALL CHECKS PASSED - Proceed to Phase 0 Research

## Project Structure

### Documentation (this feature)

```text
specs/1-learnflow-components/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (to be generated)
│   ├── chat-api.yaml
│   ├── code-execution-api.yaml
│   ├── exercise-api.yaml
│   ├── struggle-detection-api.yaml
│   └── teacher-dashboard-api.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── agents/              # AI tutor agents (concept explainer, debugger, etc.)
│   ├── api/                 # FastAPI endpoints
│   ├── models/              # SQLAlchemy models (Student, Session, Exercise, etc.)
│   ├── services/            # Business logic (struggle detection, exercise generation)
│   ├── sandbox/             # Python code execution sandbox
│   └── events/              # Kafka event handlers
└── tests/
    ├── contract/            # OpenAPI contract tests
    ├── integration/         # End-to-end tests
    └── unit/                # Unit tests

frontend/
├── src/
│   ├── components/          # React components (Chat, Editor, Dashboard)
│   ├── pages/               # Next.js pages
│   ├── services/            # API clients
│   └── lib/                 # Utilities (auth, websockets)
└── tests/
    ├── integration/         # E2E tests (Playwright)
    └── unit/                # Component tests (Jest)

infrastructure/
├── k8s/                     # Kubernetes manifests (generated by skills)
├── helm/                    # Helm values (for Kafka, PostgreSQL)
└── dapr/                    # Dapr component configurations

.claude/skills/              # Existing skills (kafka-k8s-setup, postgres-k8s-setup, etc.)
```

**Structure Decision**: Web application structure selected because LearnFlow has distinct frontend (student/teacher interfaces) and backend (AI agents, sandbox, APIs). Microservices pattern enables independent scaling of compute-intensive components (code execution, exercise generation) and supports event-driven architecture for struggle detection.

## Complexity Tracking

> No constitutional violations - this section intentionally left empty.

---

## Technology Stack & Justification

### AGENTIC LAYER

#### Claude Code
**What**: AI coding assistant by Anthropic that executes commands, reads/writes files, and runs tools autonomously.

**Why Chosen**:
- LearnFlow is being built WITH Claude Code to prove AI agents can build software
- Long context window (200k tokens) handles complex multi-file operations
- Tool use capabilities enable autonomous skill execution
- Instruction-following quality ensures constitutional compliance

**Alternative Rejected**: GitHub Copilot - Code completion only, no autonomous execution or tool use

**What Breaks Without It**: The entire "AI agents build software" thesis fails. Manual development would invalidate Article IV (Agents Build, Humans Teach).

---

#### Goose
**What**: Open-source AI coding agent that executes terminal commands and modifies codebases.

**Why Chosen**:
- Demonstrates cross-agent compatibility (proves skills work with multiple agents)
- Open-source nature aligns with LearnFlow's educational mission
- Complements Claude Code for tasks requiring different interaction patterns
- Validates that skills are truly agent-agnostic

**Alternative Rejected**: Cursor - Proprietary, IDE-specific, doesn't prove cross-agent compatibility

**What Breaks Without It**: Cannot prove skills are reusable across different AI agents. Reduces credibility of "skills are the future" claim.

---

#### Skills (.claude/skills/)
**What**: Reusable, agent-executable modules following SKILL.md + REFERENCE.md + scripts/ pattern with MCP Code Execution.

**Why Chosen**:
- **THE PRODUCT** - Skills library is what LearnFlow exists to prove
- MCP pattern keeps agent context under 50 tokens (Article III compliance)
- Reusable across projects (not LearnFlow-specific)
- Enables autonomous infrastructure deployment (Article VII)
- Existing skills: kafka-k8s-setup, postgres-k8s-setup, fastapi-dapr-agent, nextjs-k8s-deploy

**Alternative Rejected**: Manual deployment scripts - Not agent-executable, pollutes context, not reusable, violates Article I

**What Breaks Without It**: The entire project fails. LearnFlow exists to prove skills work. Without skills, there's no product, no thesis, no point.

---

#### Spec-Kit Plus
**What**: Specification-driven development framework with templates for spec.md, plan.md, tasks.md, and PHR tracking.

**Why Chosen**:
- Enforces separation of WHAT (spec) from HOW (plan) from WHEN (tasks)
- PHR (Prompt History Records) track every AI decision for learning and traceability
- Constitution integration ensures every decision is validated against principles
- Enables agents to work autonomously with clear requirements

**Alternative Rejected**: Ad-hoc documentation - No structure, no traceability, no constitutional enforcement

**What Breaks Without It**: Agents cannot work autonomously without clear specs. No traceability means no learning from AI decisions. Constitutional compliance cannot be verified.

---

### FRONTEND

#### Next.js 14
**What**: React framework with server-side rendering, API routes, and file-based routing.

**Why Chosen**:
- Server-side rendering improves initial load time for students (critical for engagement)
- API routes enable backend-for-frontend pattern (simplifies auth, proxying)
- File-based routing reduces boilerplate
- Built-in TypeScript support
- Vercel deployment via nextjs-k8s-deploy skill

**Alternative Rejected**:
- Create React App - No SSR, no API routes, deprecated
- Remix - Smaller ecosystem, less mature, fewer deployment skills available

**What Breaks Without It**: Students experience slow initial loads (bad first impression). No built-in API layer means more complex auth and API proxying.

---

#### TypeScript 5.x
**What**: Typed superset of JavaScript with compile-time type checking.

**Why Chosen**:
- Catches errors before runtime (critical for AI-generated code quality)
- IDE autocomplete improves agent code generation accuracy
- Interfaces document API contracts (aligns with contract-first design)
- Refactoring safety (agents can modify code with confidence)

**Alternative Rejected**: JavaScript - No type safety, harder for agents to generate correct code, more runtime errors

**What Breaks Without It**: AI-generated frontend code has more runtime errors. Refactoring becomes risky. API contracts are undocumented.

---

#### Tailwind CSS
**What**: Utility-first CSS framework with pre-defined classes for styling.

**Why Chosen**:
- Faster development (agents can generate UI without writing custom CSS)
- Consistent design system (utility classes enforce consistency)
- Smaller bundle size (unused classes purged automatically)
- No naming conflicts (no need to invent class names)

**Alternative Rejected**:
- CSS Modules - Requires naming conventions, more boilerplate
- Styled Components - Runtime overhead, harder for agents to generate

**What Breaks Without It**: Agents spend more time writing custom CSS. Inconsistent styling across components. Larger bundle sizes.

---

#### Monaco Editor
**What**: Browser-based code editor (powers VS Code) with syntax highlighting, autocomplete, and error detection.

**Why Chosen**:
- **Required by FR-013** - "System MUST provide a code editor with Python syntax highlighting and error detection"
- Industry-standard editor (students already familiar from VS Code)
- Built-in Python language support
- Extensible for custom features (hints, inline tutor suggestions)
- Lightweight (loads faster than full IDE)

**Alternative Rejected**:
- CodeMirror - Less feature-rich, smaller ecosystem
- Ace Editor - Older, less maintained, fewer language features

**What Breaks Without It**: Cannot meet FR-013. Students get poor editing experience (no syntax highlighting, no autocomplete). Violates "learn by doing" mission.

---

#### Better Auth
**What**: Modern authentication library for Next.js with email/password, session management, and CSRF protection.

**Why Chosen**:
- **Required by clarification** - Email/password authentication with session monitoring consent
- Built for Next.js (seamless integration with API routes)
- Session-based auth (simpler than JWT for MVP)
- CSRF protection built-in (security by default)
- Consent management hooks (required for FR-002)

**Alternative Rejected**:
- NextAuth - More complex, OAuth-focused (we need simple email/password)
- Auth0 - Third-party dependency, costs money, overkill for MVP

**What Breaks Without It**: Cannot implement FR-001 (email/password auth). No session monitoring consent mechanism. Security vulnerabilities (no CSRF protection).

---

### GATEWAY

#### Kong API Gateway
**What**: Open-source API gateway with routing, rate limiting, authentication, and observability plugins.

**Why Chosen**:
- Single entry point for all backend services (simplifies frontend)
- Rate limiting prevents abuse (protects sandbox from DoS)
- Authentication plugin validates sessions before routing
- OpenTelemetry plugin for distributed tracing (FR-040 compliance)
- Kubernetes-native (deployed via Helm)

**Alternative Rejected**:
- NGINX - Requires custom Lua scripts, less feature-rich
- Traefik - Less mature plugin ecosystem
- AWS API Gateway - Cloud-specific, violates cloud-agnostic requirement

**What Breaks Without It**: Frontend must know all backend service URLs. No centralized rate limiting (sandbox vulnerable to abuse). No single point for auth validation.

---

### BACKEND SERVICES

#### FastAPI
**What**: Modern Python web framework with automatic OpenAPI generation, async support, and type validation via Pydantic.

**Why Chosen**:
- Automatic OpenAPI schema generation (enables contract-first development)
- Async support (handles concurrent student requests efficiently)
- Pydantic validation (type-safe request/response models)
- Fast performance (comparable to Node.js/Go)
- Python ecosystem (matches sandbox language, simplifies code sharing)

**Alternative Rejected**:
- Flask - No async, no automatic OpenAPI, slower
- Django - Too heavy, includes ORM we don't need (using Dapr state management)

**What Breaks Without It**: Cannot generate OpenAPI contracts automatically. Slower request handling. No type validation (more runtime errors).

---

#### OpenAI Agent SDK
**What**: Official SDK for building multi-agent systems with function calling, streaming, and context management.

**Why Chosen**:
- **Required by clarification** - "OpenAI Agent SDK with Groq open-source models"
- Multi-agent orchestration (concept explainer, debugger, exercise generator)
- Function calling for tool use (sandbox execution, database queries)
- Streaming responses (students see tutor typing in real-time)
- Context management (maintains conversation across agent handoffs)

**Alternative Rejected**:
- LangChain - More complex, heavier abstractions, slower
- Custom implementation - Reinventing the wheel, more bugs

**What Breaks Without It**: Cannot implement FR-008 (agent routing). No multi-agent orchestration. Cannot meet FR-001 (3s response time) without streaming.

---

#### Groq API (with open-source models)
**What**: Ultra-fast inference API for open-source models (Llama 3, Mixtral) with <1s response times.

**Why Chosen**:
- **Required by clarification** - "Groq open-source models"
- Free tier available (reduces costs for MVP)
- Ultra-fast inference (<1s) enables <3s total response time (SC-001)
- Open-source models (Llama 3, Mixtral) avoid vendor lock-in
- Compatible with OpenAI SDK (easy integration)

**Alternative Rejected**:
- OpenAI GPT-4 - Expensive ($0.03/1k tokens), slower (2-3s), vendor lock-in
- Self-hosted models - Requires GPU infrastructure, complex deployment

**What Breaks Without It**: Cannot meet SC-001 (<3s response time). High costs make MVP unsustainable. Vendor lock-in violates cloud-agnostic principle.

---

#### Dapr Sidecar
**What**: Distributed application runtime that provides service-to-service communication, state management, and pub/sub via sidecars.

**Why Chosen**:
- Abstracts Kafka and PostgreSQL (services don't know about infrastructure)
- Sidecar pattern (no SDK dependencies in application code)
- Automatic retries and circuit breaking (resilience by default)
- Observability built-in (OpenTelemetry integration)
- Cloud-agnostic (swap Kafka for RabbitMQ without code changes)

**Alternative Rejected**:
- Direct Kafka/PostgreSQL clients - Tight coupling, no retries, no observability
- Service mesh (Istio) - Heavier, more complex, overkill for MVP

**What Breaks Without It**: Services tightly coupled to Kafka and PostgreSQL. No automatic retries (more failures). No built-in observability. Cannot swap infrastructure without code changes.

---

### MESSAGING

#### Apache Kafka
**What**: Distributed event streaming platform for high-throughput, fault-tolerant message queuing.

**Why Chosen**:
- **Required by spec** - "Kafka for event streaming (struggle events, exercise completions)"
- Event sourcing for struggle detection (replay events for debugging)
- High throughput (handles 10k exercises/day easily)
- Persistent logs (audit trail for teacher review)
- Existing skill: kafka-k8s-setup (Article I compliance)

**Alternative Rejected**:
- RabbitMQ - Lower throughput, no event sourcing, no persistent logs
- Redis Streams - Not durable, loses data on restart

**What Breaks Without It**: Cannot implement FR-025 (struggle event logging). No audit trail for teacher review. Cannot replay events for debugging.

---

#### KRaft Mode (no Zookeeper)
**What**: Kafka's new consensus protocol that eliminates Zookeeper dependency.

**Why Chosen**:
- Simpler deployment (one less service to manage)
- Faster startup (no Zookeeper coordination)
- Lower resource usage (fewer pods in Kubernetes)
- Future-proof (Zookeeper deprecated in Kafka 4.0)

**Alternative Rejected**: Kafka with Zookeeper - More complex, higher resource usage, deprecated

**What Breaks Without It**: More complex deployment. Higher resource usage. Using deprecated architecture.

---

#### Dapr Pub/Sub Component
**What**: Dapr abstraction over Kafka that provides publish/subscribe messaging via HTTP/gRPC.

**Why Chosen**:
- Decouples services from Kafka (can swap for RabbitMQ without code changes)
- Automatic retries and dead-letter queues (resilience by default)
- CloudEvents format (standardized event schema)
- Observability built-in (traces every message)

**Alternative Rejected**: Direct Kafka clients - Tight coupling, no retries, no observability

**What Breaks Without It**: Services tightly coupled to Kafka. No automatic retries (lost messages). No standardized event format.

---

### DATABASE

#### PostgreSQL 15
**What**: Open-source relational database with ACID transactions, JSON support, and full-text search.

**Why Chosen**:
- **Required by spec** - "PostgreSQL for data persistence (student progress, sessions, exercises)"
- ACID transactions (data consistency for student progress)
- JSON columns (flexible schema for exercise metadata)
- Full-text search (search chat history, code submissions)
- Existing skill: postgres-k8s-setup (Article I compliance)

**Alternative Rejected**:
- MongoDB - No ACID transactions, eventual consistency (data loss risk)
- MySQL - Weaker JSON support, no full-text search

**What Breaks Without It**: Cannot implement FR-005 (data retention). No ACID transactions (data corruption risk). Cannot search chat history.

---

#### Bitnami Helm Chart
**What**: Production-ready Helm chart for PostgreSQL with backup, monitoring, and high availability.

**Why Chosen**:
- Production-ready (used by thousands of companies)
- Automatic backups (prevents data loss)
- Monitoring built-in (Prometheus metrics)
- High availability (replication for zero downtime)
- Used by postgres-k8s-setup skill (Article I compliance)

**Alternative Rejected**:
- Official PostgreSQL chart - Less feature-rich, no backups
- Custom deployment - Reinventing the wheel, more bugs

**What Breaks Without It**: No automatic backups (data loss risk). No monitoring (blind to issues). No high availability (downtime during failures).

---

#### Dapr State Management
**What**: Dapr abstraction over PostgreSQL that provides key-value storage via HTTP/gRPC.

**Why Chosen**:
- Decouples services from PostgreSQL (can swap for Redis without code changes)
- Automatic retries and optimistic concurrency (resilience by default)
- Observability built-in (traces every query)
- Simpler API (key-value instead of SQL)

**Alternative Rejected**: Direct PostgreSQL clients (SQLAlchemy) - Tight coupling, more complex queries, no observability

**What Breaks Without It**: Services tightly coupled to PostgreSQL. No automatic retries (lost writes). Complex SQL queries (harder for agents to generate).

---

### INFRASTRUCTURE

#### Kubernetes
**What**: Container orchestration platform for deploying, scaling, and managing containerized applications.

**Why Chosen**:
- **Required by spec** - "Kubernetes cluster for infrastructure deployment"
- Industry standard (skills are reusable across companies)
- Declarative configuration (infrastructure as code)
- Auto-scaling (handles variable student load)
- All skills target Kubernetes (Article I compliance)

**Alternative Rejected**:
- Docker Compose - No auto-scaling, no high availability, not production-ready
- AWS ECS - Cloud-specific, violates cloud-agnostic requirement

**What Breaks Without It**: Cannot use existing skills (violates Article I). No auto-scaling (poor performance under load). Not production-ready.

---

#### Minikube
**What**: Local Kubernetes cluster for development and testing.

**Why Chosen**:
- Free (no cloud costs during development)
- Fast iteration (deploy locally in seconds)
- Matches production (same Kubernetes APIs)
- All skills tested on Minikube (ensures compatibility)

**Alternative Rejected**:
- Kind - Slower startup, less feature-rich
- Docker Desktop Kubernetes - Less stable, fewer features

**What Breaks Without It**: Must use cloud Kubernetes for development (expensive, slow). Cannot test skills locally.

---

#### Helm
**What**: Package manager for Kubernetes that templates YAML manifests and manages releases.

**Why Chosen**:
- **Required by skills** - kafka-k8s-setup and postgres-k8s-setup use Helm
- Templating (reuse manifests across environments)
- Release management (rollback on failure)
- Bitnami charts (production-ready PostgreSQL, Kafka)

**Alternative Rejected**:
- Kustomize - Less powerful templating, no release management
- Raw YAML - No templating, no rollback, error-prone

**What Breaks Without It**: Cannot use Bitnami charts (must write custom manifests). No rollback (failures are permanent). Skills don't work (violates Article I).

---

#### Docker
**What**: Containerization platform for packaging applications with dependencies.

**Why Chosen**:
- **Required by Kubernetes** - All services run in containers
- Consistent environments (dev matches production)
- Isolation (sandbox cannot access host system)
- Image caching (faster builds)

**Alternative Rejected**:
- Podman - Less mature, fewer tools, not Kubernetes-native
- Virtual machines - Heavier, slower startup, more resource usage

**What Breaks Without It**: Cannot run on Kubernetes. No isolation (sandbox security risk). Inconsistent environments (dev/prod drift).

---

### MCP (Model Context Protocol)

#### MCP Servers
**What**: Servers that expose tools and resources to AI agents via standardized protocol.

**Why Chosen**:
- Standardized protocol (agents can use any MCP server)
- Tool discovery (agents learn available tools automatically)
- Context management (servers maintain state across calls)
- Extensible (add new tools without changing agent code)

**Alternative Rejected**:
- Custom tool APIs - No standardization, agents must be updated for each tool
- Function calling only - No state management, no resource discovery

**What Breaks Without It**: Agents cannot discover tools automatically. No standardized protocol (each tool requires custom integration). No state management.

---

#### MCP Code Execution Pattern
**What**: Pattern where all external calls (kubectl, API requests) are wrapped in scripts that return <50 tokens.

**Why Chosen**:
- **Required by Article III** - "Scripts MUST return under 50 tokens"
- 99.95% token savings (10,000 tokens → 5 tokens)
- Faster agent responses (less context to process)
- Prevents context limit issues (can handle more operations)
- All existing skills follow this pattern (Article I compliance)

**Alternative Rejected**:
- Direct API calls - Pollutes context with raw JSON (10,000+ tokens)
- Verbose scripts - Still wastes tokens, slower responses

**What Breaks Without It**: Agent context polluted with raw API responses (violates Article III). Slower responses. Context limit issues. Cannot handle complex operations.

---

### CI/CD

#### GitHub Actions
**What**: CI/CD platform integrated with GitHub for automated testing, building, and deployment.

**Why Chosen**:
- Free for public repos (LearnFlow is open-source)
- Integrated with GitHub (no separate platform)
- Matrix builds (test multiple Python/Node versions in parallel)
- Secrets management (store API keys securely)
- Existing workflows in skills (Article I compliance)

**Alternative Rejected**:
- Jenkins - Self-hosted (more maintenance), slower
- GitLab CI - Requires GitLab (we use GitHub)
- CircleCI - Costs money, separate platform

**What Breaks Without It**: No automated testing (more bugs). Manual deployments (slower, error-prone). No CI for skills (violates Article I).

---

## Phase 0: Research

*Research phase will be executed next to resolve any remaining technical unknowns and document best practices for each technology.*

**Research Tasks**:
1. OpenAI Agent SDK multi-agent patterns for tutor routing
2. Groq API rate limits and error handling
3. Monaco Editor Python language server integration
4. Dapr state management transaction patterns
5. Kafka topic design for struggle events
6. PostgreSQL schema design for student progress tracking
7. OpenTelemetry trace context propagation across Dapr services
8. Better Auth session monitoring consent implementation
9. Python sandbox security hardening (seccomp, AppArmor)
10. Kong rate limiting configuration for sandbox protection

---

*This plan will be completed in Phase 1 with data-model.md, contracts/, and quickstart.md generation.*
