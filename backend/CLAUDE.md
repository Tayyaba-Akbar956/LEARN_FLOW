# CLAUDE.md — Backend (LearnFlow)

## What This Is
This is the backend of LearnFlow — an AI-powered Python tutoring platform.
All 6 microservices live inside the monorepo at `/backend`.
Both Claude Code and Goose work in this directory.

---

## Monorepo Location
```
learnflow-app/
├── frontend/          ← Next.js frontend
├── backend
/          ← YOU ARE HERE
│   ├── triage-agent/
│   ├── concepts-agent/
│   ├── debug-agent/
│   ├── code-review-agent/
│   ├── exercise-agent/
│   └── progress-agent/
├── k8s/               ← kubernetes manifests
├── .claude/skills/    ← skills used to build and deploy
└── CLAUDE.md          ← root context
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework for all 6 microservices |
| Python 3.11 | Runtime for all services |
| Pydantic | Request/response validation and data models |
| SQLAlchemy | ORM for PostgreSQL |
| Alembic | Database migrations |
| python-dotenv | Environment variable management |
| Dapr SDK | Pub/sub, state management, service invocation |
| OpenAI SDK | AI agent intelligence (gpt-4o model) |
| pytest | Testing framework for all services |
| httpx | Async HTTP client for testing FastAPI |

---

## Every Service Has This Structure
```
services/<service-name>/
├── main.py                  ← FastAPI app entry point
├── requirements.txt         ← pinned dependencies
├── Dockerfile               ← container definition
├── .env.example             ← required environment variables
├── k8s-deployment.yaml      ← K8s Deployment + Service + Dapr annotations
├── routers/                 ← FastAPI route handlers
│   └── <feature>.py
├── models/                  ← SQLAlchemy models
│   └── <model>.py
├── schemas/                 ← Pydantic schemas
│   └── <schema>.py
├── services/                ← business logic layer
│   └── <logic>.py
├── db/                      ← database connection
│   └── session.py
├── tests/                   ← ALL tests live here
│   ├── conftest.py
│   ├── test_<feature>.py
│   └── test_<endpoint>.py
└── alembic/                 ← migrations
    └── versions/
```

---

## The 6 Microservices

### triage-agent
Routes all student queries to the correct specialist agent.
Entry point for every student interaction.

Routing rules:
```
"explain", "what is", "how does", "how do"  → concepts-agent
"error", "bug", "traceback", "not working"  → debug-agent
"review", "check my code", "feedback"       → code-review-agent
"quiz", "test me", "exercise", "practice"   → exercise-agent
"progress", "how am I doing", "my score"    → progress-agent
no match                                    → ask clarifying question
```

Publishes to Kafka: `learning.events` after every route decision.

---

### concepts-agent
Explains Python concepts using OpenAI gpt-4o.
Adapts explanation level to student mastery score.

```
mastery 0-40%   → beginner explanation
mastery 41-70%  → intermediate explanation
mastery 71-100% → advanced explanation
```

Publishes to Kafka: `learning.events`

---

### debug-agent
Helps students debug Python errors.
Pedagogical approach: hints before solutions.

```
error seen 0-2 times → hint only, no solution
error seen 3+ times  → full solution + explanation
error seen 3+ times  → also publish to struggle.alerts
```

Publishes to Kafka: `learning.events`, `struggle.alerts`

---

### code-review-agent
Reviews Python code on 4 dimensions:
correctness, PEP 8 style, efficiency, readability.
Returns score 1-10 per dimension + overall score.
Updates `progress.code_quality` in PostgreSQL.

Publishes to Kafka: `learning.events`, `code.submissions`

---

### exercise-agent
Generates Python exercises based on module + topic.
Auto-grades student solutions using sandbox execution.
Updates `progress.exercise_score` in PostgreSQL.
Publishes struggle alert after 3 consecutive failures.

Publishes to Kafka: `exercise.completions`, `struggle.alerts`

---

### progress-agent
Calculates mastery scores from PostgreSQL data.
Owns the mastery formula — no other service calculates mastery.

```python
mastery = (exercise_score * 0.4) + (quiz_score * 0.3) + \
          (code_quality * 0.2) + (streak * 0.1)
```

Mastery levels:
```
0-40%   → beginner   (red)
41-70%  → learning   (yellow)
71-90%  → proficient (green)
91-100% → mastered   (blue)
```

---

## Database

### Connection (same pattern in every service)
```python
# db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Environment variable required in every service
```
DATABASE_URL=postgresql://learnflow:learnflow123@postgresql.postgres.svc.cluster.local:5432/learnflow
```

### Tables (managed by Alembic — never modify manually)
```
users        → id, email, role, name, created_at
progress     → id, user_id, module, topic, mastery_score,
               exercise_score, quiz_score, code_quality,
               streak_days, updated_at
submissions  → id, user_id, code, language, result,
               output, error_msg, submitted_at
sessions     → id, user_id, started_at, ended_at, messages(JSONB)
quizzes      → id, user_id, module, score, answers(JSONB), taken_at
```

---

## Dapr Configuration

Every service MUST have these K8s annotations:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "8000"
```

Pub/sub component name: `learnflow-pubsub`
State store name: `learnflow-statestore`

### Publishing to Kafka via Dapr
```python
from dapr.clients import DaprClient
import json

def publish_event(topic: str, data: dict):
    with DaprClient() as client:
        client.publish_event(
            pubsub_name="learnflow-pubsub",
            topic_name=topic,
            data=json.dumps(data)
        )
```

### Kafka Topics
```
learning.events      → publish after every agent action
code.submissions     → publish after every code run
exercise.completions → publish after exercise graded
struggle.alerts      → publish when struggle detected
```

### Struggle Alert Format (always use exactly this)
```json
{
  "student_id": "<id>",
  "student_name": "<name>",
  "trigger": "<trigger_type>",
  "topic": "<current_topic>",
  "timestamp": "<iso_timestamp>",
  "details": "<what happened>"
}
```

---

## Every Service Exposes These Endpoints

```python
# Required in every service — no exceptions
@app.get("/health")
def health():
    return {"status": "ok", "service": "<service-name>"}

@app.post("/invoke")
async def invoke(payload: InvokeRequest):
    # main service logic here
    pass
```

---

## Pydantic Schemas Pattern

```python
# schemas/invoke.py
from pydantic import BaseModel
from typing import Optional

class InvokeRequest(BaseModel):
    query: str
    student_id: str
    mastery_score: Optional[float] = None

class InvokeResponse(BaseModel):
    result: str
    agent: str
    event_published: bool
```

---

## Code Sandbox Rules (exercise-agent + code page)

```python
import subprocess

def run_code(code: str) -> dict:
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=5,          # 5 second hard limit
            # no network, no fs access beyond /tmp
        )
        return {
            "output": result.stdout,
            "error": result.stderr or None,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Execution timed out (5 second limit)",
            "exit_code": 1
        }
```

Forbidden in student code:
```
os.system, subprocess, socket, requests,
urllib, open (outside /tmp)
```

---

## TDD Rules — Non-Negotiable

```
1. Write test file FIRST — before any implementation
2. Run tests → confirm FAIL (red phase)
3. Write minimum code to make tests pass
4. Run tests → confirm PASS (green phase)
5. Refactor if needed → tests must still pass
6. Commit format:
   "Claude: red <service> tests written"
   "Claude: green <service> tests passing using fastapi-dapr-agent skill"
```

---

## Testing Pattern

```python
# tests/conftest.py — same in every service
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_db():
    with patch("db.session.get_db") as mock:
        yield mock

@pytest.fixture
def mock_dapr():
    with patch("dapr.clients.DaprClient") as mock:
        yield mock
```

```python
# tests/test_health.py — required in every service
def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

Run tests:
```bash
cd services/<service-name>
pytest                    # run all tests
pytest -v                 # verbose
pytest --cov=.            # with coverage
pytest tests/test_x.py    # specific file
```

---

## Environment Variables (every service needs these)

```
DATABASE_URL=postgresql://learnflow:learnflow123@postgresql.postgres.svc.cluster.local:5432/learnflow
OPENAI_API_KEY=<key>          # only services that call OpenAI
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
SERVICE_NAME=<service-name>
```

Always use python-dotenv:
```python
from dotenv import load_dotenv
import os
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
```

---

## Deployment

Use `fastapi-dapr-agent` skill only. Never deploy manually.

```bash
# From monorepo root
python .claude/skills/fastapi-dapr-agent/scripts/scaffold.py <service-name>
bash .claude/skills/fastapi-dapr-agent/scripts/deploy.sh <service-name>
python .claude/skills/fastapi-dapr-agent/scripts/verify.py <service-name>
```

Namespace: `learnflow`
All 6 services deploy to the same namespace.

---

## DO and DON'T

| ✅ DO | ❌ DON'T |
|---|---|
| Write tests before every endpoint | Write endpoints without tests |
| Use Pydantic for all request/response | Use raw dicts for API contracts |
| Use SQLAlchemy for all DB access | Write raw SQL (except migrations) |
| Use Alembic for schema changes | Modify tables manually |
| Publish to Kafka after every action | Skip Kafka events |
| Use Dapr for all service communication | Call other services directly via HTTP |
| Use python-dotenv for all config | Hardcode any values |
| Use `fastapi-dapr-agent` skill to deploy | Write K8s manifests manually |
| Check student_id exists before processing | Assume student exists |
| Return minimal output from scripts | Let raw DB/API responses enter context |