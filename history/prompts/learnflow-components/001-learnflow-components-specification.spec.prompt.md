---
id: 001
title: LearnFlow Components Specification
stage: spec
date: 2026-02-21
surface: agent
model: claude-opus-4-6
feature: learnflow-components
branch: 1-learnflow-components
user: tayyaba
command: /sp.specify
labels: ["specification", "components", "human-needs", "learnflow", "chat-interface", "code-editor", "exercise-system", "struggle-detection", "teacher-dashboard", "skills-library"]
links:
  spec: specs/1-learnflow-components/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/1-learnflow-components/spec.md
  - specs/1-learnflow-components/checklists/requirements.md
tests:
  - N/A (specification phase)
---

## Prompt

sp.specify answers these questions for every component:

  WHY does this component exist?
  WHAT human problem does it solve?
  WHAT does success feel like to the person using it?
  WHAT must never happen to this component?
  HOW does it serve the larger purpose of LearnFlow?

It does NOT answer:
  Which framework to use
  Which endpoint to build
  Which database table to create
  How to deploy it

Those are implementation details. The spec is above all of that.

═══════════════════════════════════════════════
THE HUMAN PROBLEMS LEARNFLOW SOLVES
═══════════════════════════════════════════════

PROBLEM 1 — The student learning alone
  Learning to code is hard and lonely.
  When a student is stuck, they have nobody to ask.
  They sit with an error for hours, feeling stupid.
  LearnFlow means there is always someone there.
  Always patient. Always available. Never judging.

PROBLEM 2 — The gap between tutorial and practice
  Students watch videos and read docs.
  But they cannot learn to code without writing code.
  LearnFlow puts the editor next to the tutor.
  The student learns by doing, not by watching.

PROBLEM 3 — AI that gives answers instead of teaching
  Most AI tools give you the answer immediately.
  That feels helpful but produces no learning.
  LearnFlow's agents are tutors, not answer machines.
  They guide. They hint. They ask questions back.
  They only give answers when the student has truly struggled.

═══════════════════════════════════════════════
WRITE sp.specify FOR EACH COMPONENT BELOW
═══════════════════════════════════════════════

For each component, write a specification that covers:

  PURPOSE     — why this exists in one sentence
  HUMAN NEED  — the specific human problem this solves
  EXPERIENCE  — what the person feels when it works (not technically but emotionally)
  MUST NEVER  — what would make this component a failure
  MISSION FIT — how this serves LearnFlow's threefold mission

COMPONENT 1: The Chat Interface (Triage + All Agents)
  Why does a student chat instead of search or read docs?
  What makes a good tutor conversation vs a bad one?
  What is the difference between this and just using ChatGPT?

COMPONENT 2: The Code Editor (Monaco + Sandbox)
  Why is the editor in the same place as the tutor?
  What happens when a student can write and run code without leaving?
  What is the risk of a bad sandbox experience?

COMPONENT 3: The Exercise System
  Why do students need exercises generated for them?
  What makes a good exercise vs a bad one for learning?
  What is the right moment to offer an exercise?

COMPONENT 4: The Struggle Detection System
  Why is detecting struggle more important than detecting success?
  What is the human cost of undetected struggle?
  What is the difference between productive struggle and harmful struggle?

COMPONENT 5: The Teacher Dashboard
  Why does the teacher need a dashboard at all?
  What decision does the teacher make when they see a struggle alert?
  What is the relationship between the teacher and the AI agents?

COMPONENT 6: The Skills Library
  Why are skills the product and not the app?
  What does it mean for a skill to be truly reusable?
  How does each skill serve LearnFlow's agentic mission?

═══════════════════════════════════════════════
FORMAT
═══════════════════════════════════════════════

Write each component specification as a formal sp.specify entry with:

  COMPONENT NAME
  ─────────────
  Purpose:      one sentence

  Human Need:   the real problem this solves for a real person

  Experience:   "When this works perfectly, the user feels..."

  Must Never:   "This component fails if the user ever..."

  Mission Fit:  how this connects to the larger LearnFlow mission

Keep each specification under 200 words but complete enough that an agent can understand the human purpose without asking clarifying questions.

## Response snapshot

Created comprehensive LearnFlow Core Components specification with:

**6 Component Specifications**:
1. Chat Interface - Conversational tutor providing guided discovery learning
2. Code Editor - Seamless learn-by-doing with integrated sandbox execution
3. Exercise System - Adaptive, personalized practice at optimal difficulty
4. Struggle Detection - Proactive identification of students needing help
5. Teacher Dashboard - Human oversight and intervention for edge cases
6. Skills Library - Reusable agent-executable deployment modules

**5 User Stories** (prioritized P1-P3):
- P1: Student gets unstuck through guided conversation
- P1: Student learns by doing, not watching
- P2: Student practices with adaptive exercises
- P2: Teacher intervenes when AI can't help
- P3: Developer deploys LearnFlow using skills

**31 Functional Requirements** across all components covering chat routing, code execution, exercise generation, struggle detection, teacher alerts, and skills deployment.

**14 Success Criteria** - all measurable and technology-agnostic (e.g., "80% of questions result in discovery-based learning", "code execution within 5 seconds", "95% of infrastructure deployed via skills").

Each component specification addresses WHY it exists, WHAT human problem it solves, WHAT the user FEELS when it works, WHAT must NEVER happen, and HOW it serves LearnFlow's threefold mission.

## Outcome

- ✅ Impact: Created foundational specification defining all LearnFlow components from human-centered perspective
- 🧪 Tests: Specification quality checklist created and validated (all checks passed)
- 📁 Files: specs/1-learnflow-components/spec.md, specs/1-learnflow-components/checklists/requirements.md
- 🔁 Next prompts: Ready for `/sp.plan` to design technical architecture, or `/sp.clarify` if refinements needed
- 🧠 Reflection: Specification successfully focuses on human needs and emotional outcomes rather than technical implementation, providing clear foundation for planning phase

## Evaluation notes (flywheel)

- Failure modes observed: None - specification complete without clarifications needed
- Graders run and results (PASS/FAIL): Requirements quality checklist PASS (all 12 items validated)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed to planning phase to translate human-centered spec into technical architecture
