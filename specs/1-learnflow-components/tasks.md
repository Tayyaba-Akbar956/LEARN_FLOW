---
description: "Task list for LearnFlow Core Components implementation"
---

# Tasks: LearnFlow Core Components

**Input**: Design documents from `/specs/1-learnflow-components/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: Tests are NOT included in this task list as they were not explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below follow web application structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend project structure (backend/src/{agents,api,models,services,sandbox,events})
- [X] T002 Create frontend project structure (frontend/src/{components,pages,services,lib})
- [X] T003 Initialize Python 3.11 project with FastAPI, OpenAI SDK, SQLAlchemy dependencies in backend/pyproject.toml
- [X] T004 Initialize Next.js 14 project with TypeScript, Tailwind CSS, Monaco Editor in frontend/package.json
- [X] T005 [P] Configure pytest in backend/pytest.ini
- [X] T006 [P] Configure Jest and React Testing Library in frontend/jest.config.js
- [X] T007 [P] Configure ESLint and Prettier in frontend/.eslintrc.json
- [X] T008 [P] Configure Black and isort in backend/pyproject.toml
- [X] T009 Create .gitignore for Python and Node.js
- [X] T010 Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T011 Deploy Kafka using kafka-k8s-setup skill (verify with skill's verification script)
- [x] T012 Deploy PostgreSQL using postgres-k8s-setup skill (verify with skill's verification script)
- [x] T013 Create Kafka topics (learning.events, code.submissions, exercise.completions, struggle.alerts) using kafka-k8s-setup skill
- [x] T014 Run PostgreSQL migrations using postgres-k8s-setup skill
- [x] T015 [P] Configure Dapr pub/sub component for Kafka in infrastructure/dapr/pubsub.yaml
- [x] T016 [P] Configure Dapr state management component for PostgreSQL in infrastructure/dapr/statestore.yaml
- [x] T017 [P] Deploy Kong API Gateway using Helm in infrastructure/helm/kong-values.yaml
- [x] T018 [P] Configure OpenTelemetry collector in infrastructure/k8s/otel-collector.yaml
- [x] T019 Create database schema (users, sessions, exercises, struggle_events, teacher_alerts) in backend/src/models/schema.sql
- [x] T020 [P] Implement Better Auth configuration in frontend/src/lib/auth.ts
- [x] T021 [P] Create authentication middleware in backend/src/api/middleware/auth.py
- [X] T022 [P] Implement session monitoring consent UI in frontend/src/components/ConsentDialog.tsx
- [x] T023 [P] Configure OpenTelemetry SDK in backend/src/lib/telemetry.py
- [X] T024 [P] Configure OpenTelemetry SDK in frontend/src/lib/telemetry.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Student Gets Unstuck Through Guided Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable students to ask questions and receive guided, discovery-based responses from AI tutor agents

**Independent Test**: Student describes a coding problem, tutor responds with guiding questions (not immediate answers), escalates help based on struggle detection

### Implementation for User Story 1

- [X] T025 [P] [US1] Create Student model in backend/src/models/student.py
- [X] T026 [P] [US1] Create Session model in backend/src/models/session.py
- [X] T027 [P] [US1] Create Message model (chat history) in backend/src/models/message.py
- [X] T028 [US1] Implement StudentService (CRUD operations) in backend/src/services/student_service.py
- [X] T029 [US1] Implement SessionService (create, retrieve, update session) in backend/src/services/session_service.py
- [X] T030 [US1] Configure OpenAI Agent SDK client with Groq API in backend/src/agents/client.py
- [X] T031 [P] [US1] Implement ConceptExplainerAgent in backend/src/agents/concept_explainer.py
- [X] T032 [P] [US1] Implement DebuggerAgent in backend/src/agents/debugger.py
- [X] T033 [P] [US1] Implement HintProviderAgent in backend/src/agents/hint_provider.py
- [X] T034 [US1] Implement TriageService (routes questions to appropriate agent) in backend/src/services/triage_service.py
- [X] T035 [US1] Implement ChatService (manages conversation, agent handoffs, context) in backend/src/services/chat_service.py
- [X] T036 [US1] Create POST /api/chat/message endpoint in backend/src/api/chat.py
- [X] T037 [US1] Create GET /api/chat/history endpoint in backend/src/api/chat.py
- [X] T038 [US1] Create WebSocket /api/chat/stream endpoint for real-time responses in backend/src/api/chat.py
- [X] T039 [P] [US1] Implement ChatInterface component in frontend/src/components/Chat/ChatInterface.tsx
- [X] T040 [P] [US1] Implement MessageList component in frontend/src/components/Chat/MessageList.tsx
- [X] T041 [P] [US1] Implement MessageInput component in frontend/src/components/Chat/MessageInput.tsx
- [X] T042 [US1] Implement chat API client with WebSocket support in frontend/src/services/chatService.ts
- [X] T043 [US1] Create student chat page in frontend/src/pages/student/chat.tsx
- [X] T044 [US1] Implement agent indicator UI (shows which agent is responding) in frontend/src/components/Chat/AgentIndicator.tsx
- [X] T045 [US1] Add OpenTelemetry tracing to chat flow (question → triage → agent → response) in backend/src/services/chat_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Student Learns By Doing, Not Watching (Priority: P1)

**Goal**: Enable students to write, execute, and debug Python code in an integrated editor with sandbox execution

**Independent Test**: Student writes Python code, clicks "Run", sees results within 5 seconds, receives tutor feedback without leaving interface

### Implementation for User Story 2

- [X] T046 [P] [US2] Create CodeSubmission model in backend/src/models/code_submission.py
- [X] T047 [P] [US2] Create ExecutionResult model in backend/src/models/execution_result.py
- [X] T048 [US2] Implement SandboxService (Docker container execution with resource limits) in backend/src/sandbox/sandbox_service.py
- [X] T049 [US2] Configure sandbox resource limits (5s timeout, 256MB memory, no network/filesystem) in backend/src/sandbox/config.py
- [X] T050 [US2] Implement code execution security (seccomp, AppArmor profiles) in backend/src/sandbox/security.py
- [X] T051 [US2] Implement CodeExecutionService (validates, executes, captures output) in backend/src/services/code_execution_service.py
- [X] T052 [US2] Create POST /api/code/execute endpoint in backend/src/api/code.py
- [X] T053 [US2] Create GET /api/code/history endpoint in backend/src/api/code.py
- [x] T054 [US2] Publish code.submissions event to Kafka in backend/src/events/code_events.py
- [X] T055 [P] [US2] Implement CodeEditor component with Monaco Editor in frontend/src/components/Editor/CodeEditor.tsx
- [X] T056 [P] [US2] Configure Monaco Editor for Python (syntax highlighting, autocomplete) in frontend/src/components/Editor/monacoConfig.ts
- [X] T057 [P] [US2] Implement ExecutionResults component in frontend/src/components/Editor/ExecutionResults.tsx
- [X] T058 [P] [US2] Implement RunButton component in frontend/src/components/Editor/RunButton.tsx
- [X] T059 [US2] Implement code execution API client in frontend/src/services/codeService.ts
- [X] T060 [US2] Create student editor page with split view (editor + chat) in frontend/src/pages/student/editor.tsx
- [X] T061 [US2] Implement code persistence (auto-save to session) in frontend/src/lib/codePersistence.ts
- [X] T062 [US2] Integrate chat context with current code (tutor sees what student is working on) in backend/src/services/chat_service.py
- [X] T063 [US2] Add OpenTelemetry tracing to code execution flow in backend/src/services/code_execution_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Student Practices With Adaptive Exercises (Priority: P2)

**Goal**: Generate personalized exercises that adapt difficulty based on student performance

**Independent Test**: Student completes exercises, difficulty adapts within 2 exercises based on success rate and time taken

### Implementation for User Story 3

- [X] T064 [P] [US3] Create Exercise model in backend/src/models/exercise.py
- [X] T065 [P] [US3] Create ExerciseAttempt model in backend/src/models/exercise_attempt.py
- [X] T066 [P] [US3] Create Hint model in backend/src/models/hint.py
- [X] T067 [US3] Implement ExerciseGeneratorAgent (uses OpenAI SDK to generate exercises) in backend/src/agents/exercise_generator.py
- [X] T068 [US3] Implement DifficultyAdaptationService (tracks performance, adjusts difficulty) in backend/src/services/difficulty_service.py
- [X] T069 [US3] Implement ExerciseValidationService (checks student solutions) in backend/src/services/exercise_validation_service.py
- [X] T070 [US3] Implement HintService (progressive hints: vague → specific) in backend/src/services/hint_service.py
- [X] T071 [US3] Create POST /api/exercises/generate endpoint in backend/src/api/exercises.py
- [X] T072 [US3] Create POST /api/exercises/submit endpoint in backend/src/api/exercises.py
- [X] T073 [US3] Create GET /api/exercises/hints endpoint in backend/src/api/exercises.py
- [X] T074 [US3] Publish exercise.completions event to Kafka in backend/src/events/exercise_events.py
- [X] T075 [P] [US3] Implement ExerciseCard component in frontend/src/components/Exercise/ExerciseCard.tsx
- [X] T076 [P] [US3] Implement ExerciseInstructions component in frontend/src/components/Exercise/ExerciseInstructions.tsx
- [X] T077 [P] [US3] Implement HintButton component in frontend/src/components/Exercise/HintButton.tsx
- [X] T078 [P] [US3] Implement SubmitSolution component in frontend/src/components/Exercise/SubmitSolution.tsx
- [X] T079 [US3] Implement exercise API client in frontend/src/services/exerciseService.ts
- [X] T080 [US3] Create student exercises page in frontend/src/pages/student/exercises.tsx
- [X] T081 [US3] Implement difficulty indicator UI (shows current level) in frontend/src/components/Exercise/DifficultyIndicator.tsx
- [X] T082 [US3] Add OpenTelemetry tracing to exercise generation and validation in backend/src/services/exercise_validation_service.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Teacher Intervenes When AI Can't Help (Priority: P2)

**Goal**: Detect student struggle and alert teachers with sufficient context for intervention decisions

**Independent Test**: Simulate prolonged struggle (5 failures in 20 minutes), verify alert triggers, confirm teacher dashboard shows student context

### Implementation for User Story 4

- [X] T083 [P] [US4] Create StruggleEvent model in backend/src/models/struggle_event.py
- [X] T084 [P] [US4] Create TeacherAlert model in backend/src/models/teacher_alert.py
- [X] T085 [P] [US4] Create Teacher model in backend/src/models/teacher.py
- [X] T086 [US4] Implement StruggleDetectionService (tracks indicators: failures, time, help requests) in backend/src/services/struggle_detection_service.py
- [X] T087 [US4] Configure struggle thresholds (5 failures in 20 minutes) in backend/src/services/struggle_detection_service.py
- [X] T088 [US4] Implement AlertService (creates teacher alerts, sends notifications) in backend/src/services/alert_service.py
- [X] T089 [US4] Implement TeacherInterventionService (tracks outcomes, improves thresholds) in backend/src/services/teacher_intervention_service.py
- [X] T090 [US4] Subscribe to struggle.alerts Kafka topic in backend/src/events/struggle_events.py
- [X] T091 [US4] Create GET /api/teacher/alerts endpoint in backend/src/api/teacher.py
- [X] T092 [US4] Create GET /api/teacher/student/:id/context endpoint (code, chat, struggle indicators) in backend/src/api/teacher.py
- [X] T093 [US4] Create POST /api/teacher/message endpoint (send message to student) in backend/src/api/teacher.py
- [X] T094 [US4] Create GET /api/teacher/metrics endpoint (students online, intervention rate) in backend/src/api/teacher.py
- [X] T095 [P] [US4] Implement TeacherDashboard component in frontend/src/components/Teacher/TeacherDashboard.tsx
- [X] T096 [P] [US4] Implement AlertList component in frontend/src/components/Teacher/AlertList.tsx
- [X] T097 [P] [US4] Implement StudentContext component (shows code, chat, struggle indicators) in frontend/src/components/Teacher/StudentContext.tsx
- [X] T098 [P] [US4] Implement InterventionForm component in frontend/src/components/Teacher/InterventionForm.tsx
- [X] T099 [P] [US4] Implement MetricsPanel component in frontend/src/components/Teacher/MetricsPanel.tsx
- [X] T100 [US4] Implement teacher API client in frontend/src/services/teacherService.ts
- [X] T101 [US4] Create teacher dashboard page in frontend/src/pages/teacher/dashboard.tsx
- [X] T102 [US4] Implement real-time alert notifications (WebSocket) in frontend/src/lib/alertNotifications.ts
- [X] T103 [US4] Add human message indicator in student chat (shows when teacher intervenes) in frontend/src/components/Chat/MessageList.tsx
- [X] T104 [US4] Add OpenTelemetry tracing to struggle detection and alert flow in backend/src/services/struggle_detection_service.py

**Checkpoint**: At this point, all P1 and P2 user stories should be independently functional

---

## Phase 7: User Story 5 - Developer Deploys LearnFlow Using Skills (Priority: P3)

**Goal**: Deploy entire LearnFlow stack using existing skills with zero manual infrastructure code

**Independent Test**: Deploy full stack using only skills, verify no manual kubectl commands, confirm all services running with <50 token verification outputs

### Implementation for User Story 5

- [X] T105 [US5] Create deployment script that orchestrates all skills in infrastructure/deploy.sh
- [X] T106 [US5] Deploy chat service using fastapi-dapr-agent skill (scaffold + deploy backend/src/api/chat.py)
- [X] T107 [US5] Deploy code execution service using fastapi-dapr-agent skill (scaffold + deploy backend/src/api/code.py)
- [X] T108 [US5] Deploy exercise service using fastapi-dapr-agent skill (scaffold + deploy backend/src/api/exercises.py)
- [X] T109 [US5] Deploy teacher service using fastapi-dapr-agent skill (scaffold + deploy backend/src/api/teacher.py)
- [X] T110 [US5] Deploy frontend using nextjs-k8s-deploy skill (build + deploy frontend/)
- [X] T111 [US5] Verify all services using skill verification scripts (each returns <50 tokens)
- [X] T112 [US5] Create end-to-end deployment verification script in infrastructure/verify-deployment.sh
- [X] T113 [US5] Document deployment process in specs/1-learnflow-components/quickstart.md
- [x] T114 [US5] Add deployment status dashboard showing all services in frontend/src/pages/admin/deployment-status.tsx

**Checkpoint**: All user stories should now be independently functional and deployable via skills

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T115 [P] Update README.md with complete setup and deployment instructions
- [X] T116 [P] Add API documentation (OpenAPI/Swagger) in backend/src/api/docs.py
- [x] T117 [P] Implement data retention policy (1 year auto-deletion) in backend/src/services/data_retention_service.py
- [x] T118 [P] Implement account deletion endpoint in backend/src/api/auth.py
- [x] T119 [P] Add pre-deletion notification (30 days before auto-delete) in backend/src/services/notification_service.py
- [x] T120 [P] Configure Kong rate limiting for sandbox protection in infrastructure/helm/kong-values.yaml
- [X] T121 [P] Add error boundary components in frontend/src/components/ErrorBoundary.tsx
- [x] T122 [P] Implement loading states across all components in frontend/src/components/Loading/
- [x] T123 [P] Add accessibility attributes (ARIA labels) to all interactive components
- [x] T124 [P] Optimize bundle size (code splitting, lazy loading) in frontend/next.config.js
- [x] T125 [P] Add performance monitoring (Web Vitals) in frontend/src/lib/performance.ts
- [x] T126 [P] Create GitHub Actions workflow for CI/CD in .github/workflows/ci.yml
- [x] T127 [P] Add security scanning (Dependabot, CodeQL) in .github/workflows/security.yml
- [x] T128 Run quickstart.md validation (deploy and test all user stories)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 chat context but independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Uses US2 code editor but independently testable
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Monitors US1-3 but independently testable
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Deploys all services but independently testable

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all models for User Story 1 together:
Task T025: "Create Student model in backend/src/models/student.py"
Task T026: "Create Session model in backend/src/models/session.py"
Task T027: "Create Message model in backend/src/models/message.py"

# Launch all agents for User Story 1 together:
Task T031: "Implement ConceptExplainerAgent in backend/src/agents/concept_explainer.py"
Task T032: "Implement DebuggerAgent in backend/src/agents/debugger.py"
Task T033: "Implement HintProviderAgent in backend/src/agents/hint_provider.py"

# Launch all frontend components for User Story 1 together:
Task T039: "Implement ChatInterface component in frontend/src/components/Chat/ChatInterface.tsx"
Task T040: "Implement MessageList component in frontend/src/components/Chat/MessageList.tsx"
Task T041: "Implement MessageInput component in frontend/src/components/Chat/MessageInput.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Chat with AI tutor)
4. Complete Phase 4: User Story 2 (Code editor with sandbox)
5. **STOP and VALIDATE**: Test US1 + US2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Chat)
   - Developer B: User Story 2 (Editor)
   - Developer C: User Story 3 (Exercises)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All infrastructure deployment MUST use skills (Article I compliance)
- Follow TDD: write tests first if implementing test-driven approach later
