---
id: 001
title: LearnFlow Constitution Creation
stage: constitution
date: 2026-02-21
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: tayyaba
command: /sp.constitution
labels: ["constitution", "principles", "governance", "learnflow", "skills-first", "tdd", "autonomy"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A
---

## Prompt

LearnFlow is an AI-powered Python tutoring platform built to prove
three things simultaneously:

1. AI agents can teach humans (students learning Python)
2. AI agents can build software (Claude Code + Goose building LearnFlow)
3. Reusable skills are the future of software development

The Skills library is the real product.
LearnFlow is the proof that the skills work.

═══════════════════════════════════════════════
WRITE A CONSTITUTION THAT ANSWERS THESE:
═══════════════════════════════════════════════

1. WHY does this project exist?
   What problem does it solve?
   What does success look like?

2. WHAT can never be compromised?
   What are the absolute red lines?
   What would make this project a failure even if it "works"?

3. HOW must every decision be made?
   What principles guide architecture choices?
   What principles guide development process?
   What principles guide AI agent behaviour?

4. WHO is this for?
   What does the student experience that must never be broken?
   What does the teacher experience that must never be broken?
   What do the judges evaluate that must always be true?

═══════════════════════════════════════════════
NON-NEGOTIABLE PRINCIPLES TO ENCODE:
═══════════════════════════════════════════════

These are the principles — write them as constitution articles:

PRINCIPLE 1 — SKILLS FIRST
  Every piece of infrastructure and deployment must use a skill.
  Writing deployment code manually is a violation of this project's purpose.
  If a skill does not exist for a task, create the skill first.

PRINCIPLE 2 — TESTS BEFORE CODE (STRICT TDD)
  No implementation code exists before its test exists.
  A test that passes without implementation first is not TDD.
  This is verified by commit history — red commit must precede green commit.

PRINCIPLE 3 — MINIMAL CONTEXT (MCP CODE EXECUTION)
  No raw API or kubectl response ever enters agent context.
  Every external call is wrapped in a script.
  Scripts return under 50 tokens. Always.

PRINCIPLE 4 — AGENTS BUILD, HUMANS TEACH
  Humans write specs and principles.
  AI agents write code and deploy infrastructure.
  If a human is writing application code manually, something is wrong.

PRINCIPLE 5 — REAL BEHAVIOUR OVER FAKE DEMOS
  Every feature must work with real data.
  No hardcoded responses. d.
  It detects struggle and escalates — it does not ignore it.

PRINCIPLE 7 — AUTONOMY IS THE METRIC
  The measure of success is not "does it work" but
  "how little human intervention was needed to make it work".
  Single prompt to running deployment is the gold standard.

═══════════════════════════════════════════════
FORMAT
═══════════════════════════════════════════════

Write the constitution as a formal document with:
* A preamble explaining why this constitution exists
* Numbered articles, one per principle
* Each article has: title, statement, rationale, and what violates it
* A closing section on how to resolve conflicts using the constitution

The constitution must be written so that Claude Code or Goose
can read it and make correct decisions WITHOUT asking for clarification.

Write the constitution now.

## Response snapshot

Created comprehensive LearnFlow Skills Library Constitution v1.0.0 with:

**Preamble**: Establishes threefold mission (AI teaches humans, AI builds software, skills are the future) and defines success/failure criteria.

**Seven Articles**:
- Article I: Skills First - All infrastructure must use skills; manual deployment violates project purpose
- Article II: Tests Before Code - Strict TDD with red-green-refactor verified by commit history
- Article III: Minimal Context - MCP pattern with <50 token script outputs; no raw API responses
- Article IV: Agents Build, Humans Teach - Clear separation: humans write specs, agents write code
- Article V: Real Behavior Over Fake Demos - No hardcoded responses; real data only
- Article VI: Adaptive Learning - Real-time struggle detection and teacher escalation
- Article VII: Autonomy Is The Metric - Success measured by minimal human intervention

**Conflict Resolution**: Hierarchical principle ordering for decision-making with concrete examples.

**Governance**: Amendment process, compliance enforcement, versioning rules, and agent authority.

Constitution is machine-readable for autonomous agent decision-making without human clarification.

## Outcome

- ✅ Impact: Created foundational governance document defining all project principles and decision-making framework
- 🧪 Tests: N/A (governance document)
- 📁 Files: .specify/memory/constitution.md (created/overwritten)
- 🔁 Next prompts: Review template alignment, begin feature specification with constitutional principles
- 🧠 Reflection: Constitution successfully encodes all seven principles as enforceable articles with clear violation criteria and conflict resolution hierarchy

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual review required for constitutional alignment
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Apply constitution to first feature specification to validate enforceability
