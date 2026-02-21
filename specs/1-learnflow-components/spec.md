# Feature Specification: LearnFlow Core Components

**Feature Branch**: `1-learnflow-components`
**Created**: 2026-02-21
**Status**: Draft
**Input**: User description: "Comprehensive specifications for all LearnFlow components focusing on human needs and emotional outcomes"

## Clarifications

### Session 2026-02-21

- Q: How should students authenticate to access LearnFlow, and what privacy controls must they have? → A: Email/password with explicit session monitoring consent
- Q: Which AI model provider(s) should LearnFlow use for tutor agents? → A: OpenAI Agent SDK with Groq open-source models
- Q: How long should student learning data (progress, sessions, code history) be retained? → A: 1 year with auto-deletion after inactivity
- Q: What observability approach should LearnFlow use for monitoring, logging, and debugging? → A: Structured logging with OpenTelemetry
- Q: What resource limits should be enforced on student code execution in the sandbox? → A: 5 second timeout, 256MB memory, no network/filesystem

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Student Gets Unstuck Through Guided Conversation (Priority: P1)

A student learning Python is stuck on a list comprehension error. Instead of searching Stack Overflow or reading docs alone, they open LearnFlow and describe their problem in natural language. The AI tutor asks clarifying questions, guides them to discover the issue themselves, and only provides direct help after detecting genuine struggle.

**Why this priority**: This is the core value proposition - eliminating the loneliness and frustration of learning to code alone. Without this, LearnFlow is just another code editor.

**Independent Test**: Can be fully tested by having a student describe a coding problem and verifying the tutor responds with questions rather than immediate answers, escalating help appropriately based on struggle detection.

**Acceptance Scenarios**:

1. **Given** a student is stuck on a syntax error, **When** they describe the problem in chat, **Then** the tutor asks clarifying questions about what they've tried before giving the answer
2. **Given** a student has struggled for 10+ minutes, **When** the tutor detects repeated failures, **Then** the tutor provides more direct guidance while still encouraging learning
3. **Given** a student asks "what's wrong with my code?", **When** the tutor responds, **Then** the response guides discovery rather than stating the answer immediately

---

### User Story 2 - Student Learns By Doing, Not Watching (Priority: P1)

A student wants to practice loops. Instead of watching a video tutorial, they write code directly in LearnFlow's editor, run it immediately, see results, and get feedback from the AI tutor without leaving the interface. The editor and tutor are side-by-side, creating a seamless learn-by-doing experience.

**Why this priority**: Bridges the gap between passive learning (videos/docs) and active practice. This is what makes LearnFlow a learning platform, not just a chatbot.

**Independent Test**: Can be fully tested by having a student write code, execute it, see results, and receive tutor feedback all within one interface without external tools.

**Acceptance Scenarios**:

1. **Given** a student writes Python code in the editor, **When** they click "Run", **Then** the code executes in a sandbox and results appear within 2 seconds
2. **Given** a student's code produces an error, **When** execution completes, **Then** the error message appears clearly and the tutor offers contextual help
3. **Given** a student is working on an exercise, **When** they switch between editor and chat, **Then** the tutor maintains context about their current code

---

### User Story 3 - Student Practices With Adaptive Exercises (Priority: P2)

A student has just learned about functions. The AI tutor generates a personalized exercise at the right difficulty level based on their progress. If the student completes it easily, the next exercise is harder. If they struggle, the tutor adjusts difficulty down and provides scaffolding.

**Why this priority**: Personalized practice is what makes AI tutoring superior to static tutorials. This ensures students are always in the "zone of proximal development" - challenged but not overwhelmed.

**Independent Test**: Can be fully tested by completing exercises and verifying that difficulty adapts based on performance, with exercises generated dynamically rather than from a fixed bank.

**Acceptance Scenarios**:

1. **Given** a student completes an exercise quickly with no errors, **When** they request the next exercise, **Then** the difficulty increases appropriately
2. **Given** a student fails an exercise twice, **When** they try again, **Then** the tutor provides hints or simplifies the problem
3. **Given** a student is learning a new concept, **When** they request an exercise, **Then** the exercise is generated to match their current skill level and recent topics

---

### User Story 4 - Teacher Intervenes When AI Can't Help (Priority: P2)

A student has been stuck on the same problem for 20 minutes despite AI guidance. The struggle detection system alerts a human teacher via the dashboard. The teacher sees the student's code, chat history, and struggle indicators, then decides whether to intervene immediately or let the student continue productive struggle.

**Why this priority**: Proves that AI agents can teach but also know their limits. Human teachers are the safety net, ensuring no student is abandoned when truly stuck.

**Independent Test**: Can be fully tested by simulating prolonged struggle, verifying the alert triggers, and confirming the teacher dashboard shows sufficient context for intervention decisions.

**Acceptance Scenarios**:

1. **Given** a student has failed the same exercise 5 times in 20 minutes, **When** the struggle threshold is exceeded, **Then** a teacher receives an alert with student context
2. **Given** a teacher receives a struggle alert, **When** they open the dashboard, **Then** they see the student's code, chat history, and struggle indicators
3. **Given** a teacher decides to intervene, **When** they send a message, **Then** the student receives it in their chat interface with clear indication it's from a human

---

### User Story 5 - Developer Deploys LearnFlow Using Skills (Priority: P3)

A developer wants to deploy the LearnFlow platform. Instead of manually writing Kubernetes manifests, Helm charts, and deployment scripts, they use the Skills library. Each infrastructure component (Kafka, PostgreSQL, FastAPI services, Next.js frontend) is deployed via a skill with a single command.

**Why this priority**: Proves the Skills library is the real product. LearnFlow exists to demonstrate that AI agents can build and deploy complex systems autonomously using reusable skills.

**Independent Test**: Can be fully tested by deploying the entire LearnFlow stack using only skills, verifying no manual infrastructure code was written, and confirming all services are running.

**Acceptance Scenarios**:

1. **Given** a developer has Kubernetes running, **When** they execute the kafka-k8s-setup skill, **Then** Kafka is deployed and verified without manual kubectl commands
2. **Given** infrastructure is deployed, **When** a developer creates a new microservice using fastapi-dapr-agent skill, **Then** the service is scaffolded, deployed, and integrated without manual code
3. **Given** all services are deployed, **When** a developer runs verification scripts, **Then** each script returns under 50 tokens confirming service health

---

### Edge Cases

- What happens when a student asks the same question repeatedly without attempting to solve it themselves?
- How does the system handle a student who is genuinely stuck vs. a student who is lazy and wants answers?
- What happens when the sandbox execution times out or crashes?
- How does the teacher dashboard handle multiple simultaneous struggle alerts?
- What happens when a skill deployment fails mid-execution?
- How does the system handle a student who leaves mid-exercise and returns hours later?

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Privacy

- **FR-001**: System MUST authenticate students via email/password registration
- **FR-002**: Registration MUST include an explicit consent checkbox for session monitoring (code, chat, struggle detection)
- **FR-003**: Students MUST be able to view and revoke session monitoring consent at any time
- **FR-004**: System MUST allow students to delete their account and all associated data
- **FR-005**: System MUST retain student learning data (progress, sessions, code history) for 1 year from last activity
- **FR-006**: System MUST automatically delete student data after 1 year of account inactivity
- **FR-007**: System MUST notify students 30 days before auto-deletion with option to retain data by logging in

#### Chat Interface (Triage + All Agents)

- **FR-008**: System MUST route student questions to the appropriate specialized agent (concept explainer, debugger, exercise generator, etc.)
- **FR-009**: System MUST maintain conversation context across agent handoffs so students don't repeat themselves
- **FR-010**: Tutor agents MUST respond with guiding questions before providing direct answers
- **FR-011**: System MUST detect when a student is asking for answers without attempting to learn and adjust tutoring strategy
- **FR-012**: Chat interface MUST display clear indicators when switching between AI agents and human teachers

#### Code Editor (Monaco + Sandbox)

- **FR-013**: System MUST provide a code editor with Python syntax highlighting and error detection
- **FR-014**: System MUST execute student code in an isolated sandbox environment that prevents system access
- **FR-015**: Code execution MUST complete within 5 seconds or timeout with a clear message
- **FR-016**: System MUST display execution results (stdout, stderr, return values) clearly in the interface
- **FR-017**: Editor MUST preserve student code across sessions so work is never lost
- **FR-018**: System MUST prevent execution of malicious code (infinite loops, file system access, network calls)
- **FR-019**: Sandbox MUST enforce resource limits: 5 second timeout, 256MB memory maximum, no network access, no filesystem access

#### Exercise System

- **FR-020**: System MUST generate exercises dynamically based on student's current skill level and recent topics
- **FR-021**: Each exercise MUST include clear instructions, expected outcomes, and success criteria
- **FR-022**: System MUST validate student solutions automatically and provide feedback
- **FR-023**: Exercise difficulty MUST adapt based on student performance (success rate, time taken, hints requested)
- **FR-024**: System MUST offer hints progressively - starting vague, becoming more specific with each request

#### Struggle Detection System

- **FR-025**: System MUST track struggle indicators: repeated failures, time spent, help requests, error patterns
- **FR-026**: System MUST distinguish between productive struggle (learning) and harmful struggle (frustration)
- **FR-027**: System MUST escalate to human teacher when struggle exceeds thresholds (e.g., 5 failures in 20 minutes)
- **FR-028**: Struggle detection MUST run in real-time without requiring manual student reporting
- **FR-029**: System MUST log all struggle events for teacher review and system improvement

#### Teacher Dashboard

- **FR-030**: Dashboard MUST display real-time struggle alerts with student context (code, chat history, struggle indicators)
- **FR-031**: Teachers MUST be able to view any student's current session (code, chat, progress) with student privacy consent
- **FR-032**: Dashboard MUST allow teachers to send messages directly to students in their chat interface
- **FR-033**: System MUST track teacher intervention outcomes to improve AI tutor escalation thresholds
- **FR-034**: Dashboard MUST show aggregate metrics (students online, average struggle time, intervention rate)

#### Skills Library

- **FR-035**: Each skill MUST follow the MCP Code Execution pattern (scripts return <50 tokens)
- **FR-036**: Skills MUST be executable by AI agents without human intervention
- **FR-037**: All LearnFlow infrastructure MUST be deployable using skills (no manual deployment code)
- **FR-038**: Each skill MUST include verification scripts that confirm successful deployment
- **FR-039**: Skills MUST be reusable across projects, not LearnFlow-specific

#### Observability & Monitoring

- **FR-040**: System MUST use OpenTelemetry for distributed tracing across all services
- **FR-041**: All services MUST emit structured logs in JSON format with consistent field names
- **FR-042**: System MUST trace complete user journeys (question → agent routing → response) with correlation IDs
- **FR-043**: System MUST expose metrics for: response latency, struggle detection accuracy, exercise completion rates, teacher intervention frequency
- **FR-044**: Logs MUST include context: student ID (anonymized), session ID, agent type, timestamp, event type

### Key Entities

- **Student**: A person learning Python through LearnFlow; tracks progress, struggle history, skill level
- **Session**: A single learning session; includes code written, chat history, exercises attempted, struggle events
- **Exercise**: A dynamically generated practice problem; includes instructions, test cases, difficulty level, hints
- **Struggle Event**: A detected instance of student difficulty; includes type (repeated failure, timeout, help request), severity, timestamp
- **Teacher Alert**: A notification sent to human teacher; includes student context, struggle indicators, recommended actions
- **Skill**: A reusable deployment module; includes instructions, scripts, verification logic, token budget
- **Agent**: A specialized AI tutor (concept explainer, debugger, exercise generator); includes routing rules, response patterns

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Students can describe a coding problem and receive a helpful guiding response within 3 seconds
- **SC-002**: 80% of student questions result in discovery-based learning (questions/hints) rather than direct answers
- **SC-003**: Students can write, execute, and see results of Python code within 5 seconds without leaving the interface
- **SC-004**: Code sandbox prevents 100% of malicious code execution attempts (infinite loops, file access, network calls)
- **SC-005**: Exercise difficulty adapts within 2 exercises based on student performance
- **SC-006**: 90% of generated exercises are appropriate for student's current skill level (neither too easy nor too hard)
- **SC-007**: Struggle detection identifies students needing help within 2 minutes of threshold being exceeded
- **SC-008**: Teachers receive struggle alerts with sufficient context to make intervention decisions in under 30 seconds
- **SC-009**: 95% of LearnFlow infrastructure is deployed using skills with zero manual deployment code
- **SC-010**: All skill verification scripts return results in under 50 tokens
- **SC-011**: AI agents can deploy the entire LearnFlow stack from a single prompt with fewer than 5 clarifying questions
- **SC-012**: Students report feeling "supported, not alone" in 85% of post-session surveys
- **SC-013**: Students complete exercises at a 70% success rate (indicating appropriate difficulty)
- **SC-014**: Teacher intervention rate is below 10% of total sessions (AI handles 90%+ of tutoring)

## Assumptions

- Students have basic computer literacy and can use a web browser
- Students are learning Python specifically (not other languages initially)
- Teachers are available during learning hours to respond to struggle alerts
- Kubernetes cluster is available for skills-based deployment
- Students consent to session monitoring for struggle detection and teacher intervention
- Internet connectivity is stable for real-time chat and code execution
- Sandbox environment has sufficient resources to execute student code safely

## Out of Scope

- Support for programming languages other than Python (future enhancement)
- Mobile native apps (web interface only for MVP)
- Offline mode (requires internet for AI tutoring and code execution)
- Video tutorials or recorded lessons (focus is on interactive learning)
- Peer-to-peer student collaboration features
- Gamification elements (badges, leaderboards, achievements)
- Integration with external learning management systems (LMS)
- Payment processing or subscription management

## Dependencies

- Kubernetes cluster for infrastructure deployment
- Kafka for event streaming (struggle events, exercise completions)
- PostgreSQL for data persistence (student progress, sessions, exercises)
- Dapr for microservice communication
- Monaco Editor for code editing interface
- Python sandbox environment (containerized execution)
- OpenAI Agent SDK for tutor agent orchestration
- Groq API for open-source model inference (Llama, Mixtral, or similar)
- OpenTelemetry for distributed tracing, metrics, and structured logging

## Risks

- **Sandbox escape**: Student code could potentially break out of sandbox and access system resources
  - Mitigation: Use proven containerization (Docker), resource limits, network isolation
- **AI tutor gives answers too quickly**: Defeats the learning-by-discovery purpose
  - Mitigation: Strict prompt engineering, response validation, teacher feedback loop
- **Struggle detection false positives**: Alerts teachers unnecessarily, causing alert fatigue
  - Mitigation: Tune thresholds based on real data, allow teachers to adjust sensitivity
- **Skills deployment failures**: Infrastructure doesn't deploy correctly, blocking development
  - Mitigation: Comprehensive verification scripts, rollback procedures, manual fallback documentation
- **Student privacy concerns**: Session monitoring could feel invasive
  - Mitigation: Clear consent, anonymization options, teacher code of conduct

---

## Component Specifications

### COMPONENT 1: Chat Interface (Triage + All Agents)

**Purpose**: Provide students with a conversational tutor that guides discovery rather than giving immediate answers.

**Human Need**: Learning to code is lonely and frustrating. When stuck, students need someone patient and available who won't judge them for asking "stupid questions." They need a tutor who helps them learn, not just solves their problems.

**Experience**: "When this works perfectly, the student feels like they have a patient mentor sitting beside them. They feel safe asking questions, confident that they'll be guided to the answer rather than made to feel dumb. They feel the satisfaction of discovering solutions themselves rather than being handed answers."

**Must Never**: "This component fails if the student ever feels like they're talking to a search engine or documentation. It fails if answers come too quickly without guiding questions. It fails if the student feels judged or stupid for asking basic questions. It fails if context is lost between messages, forcing the student to repeat themselves."

**Mission Fit**: Proves AI agents can teach humans by demonstrating adaptive, patient, discovery-based tutoring that responds to individual student needs in real-time.

---

### COMPONENT 2: Code Editor (Monaco + Sandbox)

**Purpose**: Enable students to learn by doing - writing and running code immediately without leaving the tutoring interface.

**Human Need**: Students can't learn to code by watching videos or reading docs. They need to write code, run it, see what happens, and get immediate feedback. Switching between a tutorial and a separate IDE breaks flow and creates friction.

**Experience**: "When this works perfectly, the student feels like they're in a playground where experimentation is safe and instant. They write code, hit run, see results immediately, and the tutor is right there to explain what happened. There's no fear of breaking things, no setup friction, no context switching."

**Must Never**: "This component fails if the student ever loses their code due to crashes or session timeouts. It fails if execution is slow (>5 seconds) or unreliable. It fails if the sandbox allows malicious code to escape and cause harm. It fails if error messages are cryptic or unhelpful. It fails if the student has to leave the interface to test their code elsewhere."

**Mission Fit**: Bridges the gap between passive learning and active practice, proving that AI-powered platforms can provide seamless learn-by-doing experiences that traditional tutorials cannot.

---

### COMPONENT 3: Exercise System

**Purpose**: Generate personalized practice exercises at the right difficulty level to keep students in the zone of productive challenge.

**Human Need**: Static tutorials give everyone the same exercises regardless of skill level. Students need practice problems that adapt - harder when they're succeeding, easier when they're struggling, always at the edge of their current ability.

**Experience**: "When this works perfectly, the student feels challenged but not overwhelmed. Each exercise feels like it was designed specifically for them, at exactly the right difficulty. They feel progress as exercises gradually increase in complexity. They feel supported when hints arrive at just the right moment."

**Must Never**: "This component fails if the student ever receives exercises that are far too easy (boring) or far too hard (demoralizing). It fails if exercises feel generic or random rather than personalized. It fails if hints give away the answer instead of guiding discovery. It fails if the student can't tell whether their solution is correct."

**Mission Fit**: Demonstrates that AI agents can generate adaptive, personalized learning content in real-time, something impossible with static curriculum or human teachers at scale.

---

### COMPONENT 4: Struggle Detection System

**Purpose**: Identify when students are stuck and need help before they give up in frustration.

**Human Need**: Students learning alone often don't know when to ask for help. They sit with errors for hours, feeling stupid, until they quit. They need a system that notices when they're struggling and intervenes before frustration turns into abandonment.

**Experience**: "When this works perfectly, the student feels seen and supported. They don't have to admit they're stuck or ask for help - the system notices and offers assistance proactively. They feel like someone is watching out for them, ensuring they never struggle alone for too long."

**Must Never**: "This component fails if the student ever struggles for extended periods without detection. It fails if it interrupts productive struggle (when the student is learning through challenge). It fails if alerts are ignored and students are abandoned. It fails if detection is so aggressive that students feel micromanaged or not trusted to struggle productively."

**Mission Fit**: Proves AI agents can detect human emotional states (frustration, confusion) through behavioral signals and respond appropriately, demonstrating empathy and adaptive support.

---

### COMPONENT 5: Teacher Dashboard

**Purpose**: Enable human teachers to monitor AI tutoring effectiveness and intervene when students need human help.

**Human Need**: Teachers need to know which students are struggling and need human intervention. They need context (what the student is working on, what they've tried, why the AI couldn't help) to intervene effectively. They need to trust that the AI is handling most students so they can focus on those who truly need human help.

**Experience**: "When this works perfectly, the teacher feels like they have superpowers - they can see every student's progress at a glance, receive alerts only for students who truly need help, and have all the context needed to intervene effectively. They feel like a safety net, not a primary instructor, trusting the AI to handle routine tutoring."

**Must Never**: "This component fails if the teacher ever misses a student who needed help. It fails if alerts lack sufficient context, forcing teachers to investigate before helping. It fails if alert fatigue causes teachers to ignore notifications. It fails if teachers feel they need to monitor every student constantly because they don't trust the AI. It fails if student privacy is violated through excessive monitoring."

**Mission Fit**: Demonstrates the relationship between AI agents and human teachers - AI handles scale, humans handle edge cases and emotional support, proving that AI augments rather than replaces human teaching.

---

### COMPONENT 6: Skills Library

**Purpose**: Provide reusable, agent-executable deployment modules that prove AI agents can build and deploy complex infrastructure autonomously.

**Human Need**: Developers waste time writing repetitive deployment code. AI agents need reusable intelligence to operate autonomously. The industry needs proof that AI-powered development is viable at scale.

**Experience**: "When this works perfectly, the developer feels like they have a team of expert DevOps engineers who can deploy anything with a single command. They feel confident that infrastructure will be deployed correctly, consistently, and without manual intervention. They feel like they're working at a higher level of abstraction, focusing on what to build rather than how to deploy it."

**Must Never**: "This component fails if the developer ever has to write manual deployment code because a skill doesn't exist or doesn't work. It fails if skills are LearnFlow-specific and can't be reused elsewhere. It fails if agent context is polluted with raw API responses (violating the <50 token rule). It fails if skills require human intervention to execute. It fails if verification is unreliable, leaving uncertainty about deployment success."

**Mission Fit**: The Skills library IS the product. LearnFlow exists to prove that skills work. This component demonstrates that reusable, agent-executable intelligence is the future of software development, enabling AI agents to build complex systems autonomously with minimal human intervention.
