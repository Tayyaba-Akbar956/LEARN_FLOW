<!--
SYNC IMPACT REPORT
==================
Version change: [INITIAL] → 1.0.0
Modified principles: N/A (initial constitution)
Added sections: All (Preamble, Articles I-VII, Conflict Resolution, Governance)
Removed sections: None
Templates requiring updates:
  ✅ .specify/templates/plan-template.md (verified alignment)
  ✅ .specify/templates/spec-template.md (verified alignment)
  ✅ .specify/templates/tasks-template.md (verified alignment)
Follow-up TODOs: None
-->

# LearnFlow Skills Library Constitution

## Preamble

This constitution exists to ensure that the LearnFlow Skills Library project achieves its threefold mission:

1. **Prove AI agents can teach humans** through an AI-powered Python tutoring platform
2. **Prove AI agents can build software** by having Claude Code and Goose autonomously construct LearnFlow
3. **Prove reusable skills are the future** by making the Skills library the real product, with LearnFlow as proof

**The Core Thesis**: If this project succeeds, it will demonstrate that AI agents equipped with reusable skills can autonomously build and deploy production-grade cloud-native systems with minimal human intervention.

**What Success Looks Like**: A single prompt results in a fully deployed, working LearnFlow platform where students learn Python through adaptive AI tutoring, all infrastructure is deployed via skills, and every line of code follows strict TDD principles verified by commit history.

**What Failure Looks Like**: Even if the system "works," the project fails if:
- Humans wrote deployment code manually instead of using skills
- Implementation code exists without preceding tests
- Agent context is polluted with raw API responses
- Features use hardcoded responses instead of real behavior
- The deployment required extensive human intervention

This constitution is the supreme authority for all technical and process decisions. It is written to be machine-readable by AI agents, enabling autonomous decision-making without human clarification.

---

## Article I: Skills First

**Statement**: Every piece of infrastructure deployment, service orchestration, and system configuration MUST use a skill from the Skills library. Writing deployment code manually is a direct violation of this project's purpose.

**Rationale**: The Skills library is the product. LearnFlow exists to prove the skills work. If we bypass skills to "move faster," we invalidate the entire project thesis. Skills encode reusable intelligence that agents can execute autonomously across projects.

**Requirements**:
- All Kubernetes deployments MUST use skills (kafka-k8s-setup, postgres-k8s-setup, etc.)
- All service scaffolding MUST use skills (fastapi-dapr-agent, nextjs-k8s-deploy, etc.)
- All documentation generation MUST use skills (agents-md-gen, docusaurus-deploy)
- If a required skill does not exist, the skill MUST be created first before proceeding with the task

**Violations**:
- Running `kubectl apply -f deployment.yaml` directly instead of using a skill
- Writing Helm install commands in application code
- Creating Docker build scripts outside the skill pattern
- Any manual infrastructure setup that could be encoded as a skill

**Enforcement**: Code reviews and commit history audits MUST verify that all infrastructure changes reference skill execution. Pull requests containing manual deployment code MUST be rejected.

---

## Article II: Tests Before Code (Strict TDD)

**Statement**: No implementation code may exist before its test exists. A test that passes without implementation first is not TDD. This is verified by commit history—a red commit MUST precede every green commit.

**Rationale**: TDD is not optional; it is the only way to ensure that AI agents build correct, testable, and maintainable code. The red-green-refactor cycle forces clarity of requirements before implementation and provides immediate feedback on correctness.

**Requirements**:
- Every feature MUST begin with a failing test (red commit)
- Implementation code MUST be committed separately after tests fail (green commit)
- Refactoring MUST occur in a third commit after tests pass (refactor commit)
- Commit messages MUST indicate TDD phase: "red: add test for X", "green: implement X", "refactor: simplify X"
- Tests MUST fail for the right reason (missing implementation, not syntax errors)

**Violations**:
- Committing implementation code before tests exist
- Writing tests after implementation is complete
- Committing tests and implementation in the same commit
- Tests that pass immediately without implementation (false positives)
- Skipping the red phase by writing tests that don't fail first

**Enforcement**: Git hooks MUST verify commit message format. Code reviews MUST verify that red commits precede green commits in the history. Any PR without clear TDD commit sequence MUST be rejected.

---

## Article III: Minimal Context (MCP Code Execution)

**Statement**: No raw API response, kubectl output, or external service data may enter agent context. Every external call MUST be wrapped in a script. Scripts MUST return under 50 tokens. Always.

**Rationale**: Raw API responses (10,000+ tokens) cause token waste, slower responses, and context limit issues. The MCP Code Execution pattern achieves 99.95% token savings by filtering output in scripts, keeping agent context clean and focused.

**Requirements**:
- All kubectl commands MUST be wrapped in Python/Bash scripts
- All API calls MUST be wrapped in scripts that parse and filter responses
- Script output MUST be under 50 tokens (e.g., "✓ 3 Kafka pods running")
- Scripts MUST return structured, minimal status (success/failure + essential info)
- Error messages MUST be concise and actionable (under 50 tokens)

**Violations**:
- Running `kubectl get pods -o json` and loading raw JSON into context
- Making API calls directly in agent prompts
- Returning full stack traces or verbose logs to the agent
- Scripts that output more than 50 tokens
- Parsing JSON or YAML in agent context instead of in scripts

**Enforcement**: All skills MUST include verification scripts that demonstrate minimal output. Code reviews MUST reject any direct kubectl/API calls. Token usage MUST be monitored per operation.

---

## Article IV: Agents Build, Humans Teach

**Statement**: Humans write specifications and principles. AI agents write code and deploy infrastructure. If a human is writing application code manually, something is wrong.

**Rationale**: This project proves that AI agents can build software autonomously. Human intervention should be limited to high-level guidance (specs, principles, clarifications). The moment humans start writing implementation code, we've failed the autonomy test.

**Requirements**:
- Humans MUST write: specifications, constitution principles, clarifying questions, acceptance criteria
- AI agents MUST write: implementation code, tests, deployment scripts, infrastructure configuration
- Humans MAY write: example code in specs for illustration, manual test procedures for validation
- Agents MUST ask clarifying questions when specs are ambiguous rather than guessing

**Violations**:
- Humans writing Python application code for LearnFlow services
- Humans writing Kubernetes manifests or Helm charts
- Humans writing test cases (agents write tests from specs)
- Agents proceeding with implementation when requirements are unclear

**Enforcement**: Commit messages MUST indicate agent authorship (e.g., "Claude: implemented X", "Goose: deployed Y"). Code reviews MUST flag human-written implementation code. Specs MUST be complete enough for agents to implement without human code contributions.

---

## Article V: Real Behavior Over Fake Demos

**Statement**: Every feature MUST work with real data, real APIs, and real user interactions. No hardcoded responses. No mock data in production paths. No fake success messages.

**Rationale**: Demo-ware is worthless. LearnFlow must actually teach Python, actually detect student struggle, and actually escalate to teachers. If the system only appears to work, it fails the project's mission.

**Requirements**:
- All API endpoints MUST process real requests and return real data
- Student code submissions MUST be executed in real sandboxed environments
- Struggle detection MUST analyze actual student behavior patterns
- Teacher escalations MUST trigger real notifications
- Database queries MUST return actual persisted data
- Kafka events MUST be real messages, not simulated

**Violations**:
- Returning hardcoded JSON responses from API endpoints
- Simulating student struggle without analyzing real data
- Fake "success" messages that don't reflect actual system state
- Mock data in production code paths (test mocks are allowed)
- Skipping actual external service calls and pretending they succeeded

**Enforcement**: Integration tests MUST verify real data flows. Code reviews MUST reject hardcoded responses. Acceptance criteria MUST include "works with real data" validation.

---

## Article VI: Adaptive Learning (Real-Time Response)

**Statement**: The LearnFlow platform MUST adapt to student behavior in real-time. It MUST detect struggle and escalate to human teachers. Ignoring student struggle is a critical failure.

**Rationale**: An AI tutor that cannot detect when a student is stuck is not a tutor—it's a static content delivery system. Real-time adaptation and escalation are core to the educational mission.

**Requirements**:
- Student interactions MUST be analyzed for struggle indicators (repeated failures, time spent, help requests)
- Struggle detection MUST trigger adaptive responses (hints, alternative explanations, simpler exercises)
- Persistent struggle MUST escalate to human teachers via notifications
- Escalation MUST include context (student history, current exercise, struggle indicators)
- Teachers MUST be able to intervene and provide guidance
- System MUST learn from teacher interventions to improve future responses

**Violations**:
- Ignoring repeated student failures on the same exercise
- Providing the same hint repeatedly without adaptation
- Failing to escalate when a student is clearly stuck
- Escalating too early before giving the student a chance to struggle productively
- Not providing teachers with sufficient context to help effectively

**Enforcement**: Acceptance criteria MUST include struggle detection scenarios. Integration tests MUST verify escalation triggers. User testing MUST validate that real students receive appropriate help.

---

## Article VII: Autonomy Is The Metric

**Statement**: The measure of success is not "does it work" but "how little human intervention was needed to make it work." Single prompt to running deployment is the gold standard.

**Rationale**: This project exists to prove AI agents can build software autonomously. Every human intervention is a failure signal. We optimize for agent autonomy, not just functional correctness.

**Requirements**:
- Deployment workflows MUST be executable from a single agent prompt
- Agents MUST resolve ambiguities by asking targeted questions, not by requiring human code
- Error recovery MUST be automated (agents debug and fix issues)
- Documentation MUST be sufficient for agents to operate without human guidance
- Skills MUST be self-contained and composable without human orchestration

**Metrics**:
- **Gold Standard**: Single prompt → fully deployed system
- **Silver Standard**: Single prompt + 1-2 clarifying questions → deployed system
- **Bronze Standard**: Single prompt + 3-5 clarifying questions → deployed system
- **Failure**: Requires human to write code, manually fix errors, or perform deployment steps

**Violations**:
- Requiring humans to manually run deployment commands
- Agents asking for code snippets instead of writing code themselves
- Agents giving up on errors instead of debugging autonomously
- Documentation that assumes human expertise instead of agent execution

**Enforcement**: Every feature MUST document the autonomy level achieved. Retrospectives MUST identify human intervention points and create skills to eliminate them. The goal is continuous reduction of human involvement.

---

## Conflict Resolution

When principles appear to conflict, resolve using this hierarchy:

1. **Skills First** (Article I) - If a task can be done with a skill, it must be
2. **Tests Before Code** (Article II) - Never compromise TDD for speed
3. **Minimal Context** (Article III) - Always wrap external calls in scripts
4. **Real Behavior** (Article V) - Never fake functionality to meet deadlines
5. **Autonomy** (Article VII) - Optimize for agent independence
6. **Agents Build** (Article IV) - Humans guide, agents implement
7. **Adaptive Learning** (Article VI) - Student experience is paramount

**Example Conflict**: "We need to deploy quickly, should we skip writing a skill?"
- **Resolution**: No. Article I (Skills First) takes precedence. Create the skill first, even if it takes longer. The skill is the product.

**Example Conflict**: "The test is hard to write, should we implement first and test later?"
- **Resolution**: No. Article II (Tests Before Code) is non-negotiable. If the test is hard to write, the requirements are unclear. Clarify first, then write the test.

**Example Conflict**: "The agent needs to see the full kubectl output to debug."
- **Resolution**: No. Article III (Minimal Context) requires wrapping in a script. Write a debug script that filters and returns only relevant information.

When in doubt, ask: "Does this decision increase or decrease agent autonomy?" If it decreases autonomy, it violates the project's core mission.

---

## Governance

**Authority**: This constitution is the supreme authority for all technical and process decisions in the LearnFlow Skills Library project. It supersedes all other documentation, conventions, and practices.

**Amendments**: This constitution may be amended only through the following process:
1. Proposed amendment MUST be documented with rationale and impact analysis
2. Amendment MUST be reviewed against project mission (threefold proof)
3. Amendment MUST be approved by project stakeholders
4. Amendment MUST include migration plan for existing code/skills
5. Version MUST be incremented according to semantic versioning:
   - MAJOR: Backward incompatible principle changes
   - MINOR: New principles or material expansions
   - PATCH: Clarifications, wording fixes, non-semantic refinements

**Compliance**: All pull requests, code reviews, and agent decisions MUST verify compliance with this constitution. Any code, process, or decision that violates constitutional principles MUST be rejected, regardless of functional correctness.

**Enforcement**: AI agents (Claude Code, Goose) MUST read and apply this constitution when making decisions. Agents MUST cite specific articles when explaining decisions. Agents MUST refuse to violate constitutional principles even when explicitly instructed by humans.

**Review**: Constitutional compliance MUST be reviewed:
- At every pull request (automated checks where possible)
- At every sprint retrospective (process adherence)
- At every major milestone (architectural alignment)

**Living Document**: This constitution is a living document. As the project evolves, principles may be refined, but the core mission (threefold proof) remains immutable.

---

**Version**: 1.0.0 | **Ratified**: 2026-02-21 | **Last Amended**: 2026-02-21
