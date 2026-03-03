# CLAUDE.md — Frontend (LearnFlow)

## What This Is
This is the frontend of LearnFlow — an AI-powered Python tutoring platform.
It lives inside the monorepo at `/frontend`.
Both Claude Code and Goose work in this directory.

---

## Monorepo Location
```
learnflow-app/
├── frontend/          ← YOU ARE HERE
├── services/          ← backend microservices
├── k8s/               ← kubernetes manifests
├── .claude/skills/    ← skills used to build and deploy
└── CLAUDE.md          ← root context
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Next.js (App Router) | Framework — all pages live in `app/` |
| TypeScript | All files are `.tsx` or `.ts` — no `.js` files |
| Tailwind CSS | All styling — no inline styles, no CSS modules |
| shadcn/ui | Component library built on Tailwind |
| Monaco Editor | Python code editor on `/code` page |
| Better Auth | Authentication — JWT issued on login |
| Jest + React Testing Library | Unit and component tests |
| axios | HTTP calls to Kong API Gateway |

---

## Folder Structure
```
frontend/
├── app/                        ← Next.js App Router
│   ├── layout.tsx              ← root layout
│   ├── page.tsx                ← redirects to /login
│   ├── login/page.tsx
│   ├── dashboard/page.tsx
│   ├── chat/page.tsx
│   ├── code/page.tsx
│   ├── progress/page.tsx
│   └── teacher/page.tsx
├── components/                 ← reusable components
│   ├── ui/                     ← shadcn/ui components
│   ├── chat/                   ← chat-specific components
│   ├── editor/                 ← Monaco editor wrapper
│   └── progress/               ← progress bar components
├── lib/                        ← utilities and API clients
│   ├── api.ts                  ← axios instance pointing to Kong
│   ├── auth.ts                 ← Better Auth client config
│   └── utils.ts                ← shared helpers
├── hooks/                      ← custom React hooks
├── types/                      ← TypeScript type definitions
├── __tests__/                  ← all test files live here
│   ├── login.test.tsx
│   ├── dashboard.test.tsx
│   ├── chat.test.tsx
│   ├── code.test.tsx
│   ├── progress.test.tsx
│   └── teacher.test.tsx
├── public/                     ← static assets
├── jest.config.ts
├── jest.setup.ts
├── tailwind.config.ts
├── tsconfig.json
├── next.config.ts
├── package.json
└── Dockerfile
```

---

## Pages — What Each One Does

### `/login`
- Email + password login form
- Uses Better Auth to authenticate
- On success: redirect to `/dashboard`
- On failure: show red error message "Invalid credentials"
- If already logged in: redirect to `/dashboard`

### `/dashboard`
- Shows student's name, current module, mastery per module
- 8 progress bars — one per Python module
- Colour coded by mastery level:
  - 0-40% → red
  - 41-70% → yellow
  - 71-90% → green
  - 91-100% → blue
- "Continue Learning" button → `/chat`

### `/chat`
- Conversational UI — messages scroll from top, input at bottom
- On send: POST to Kong `/api/triage`
- Shows "Thinking..." spinner while waiting
- Each response labelled with agent name e.g. "Concepts Agent"
- Code in responses is syntax highlighted

### `/code`
- Monaco Editor: language=python, theme=vs-dark, height=400px
- "Run Code" button → POST to Kong `/api/sandbox`
- Output panel below editor:
  - Green border if exit_code=0
  - Red border if exit_code≠0
  - Shows stdout, stderr, execution_time_ms
- "Submit for Review" button → POST to Kong `/api/review`
- Review score + feedback appears below output panel

### `/progress`
- Module-by-module mastery breakdown
- Each module shows: name, percentage, level badge, sub-scores
- Sub-scores: Exercises (40%), Quizzes (30%), Code Quality (20%), Streak (10%)
- Overall streak counter at top

### `/teacher`
- Protected — only `role="teacher"` can access
- Student blocked → redirect to `/dashboard`
- Class overview table: Name, Module, Mastery %, Level, Last Active
- Struggle alerts panel: polls `/api/alerts` every 10 seconds
- Click student → modal with detailed progress
- Generate exercise input + assign to student

---

## API Communication

All backend calls go through Kong API Gateway.
Never call microservices directly.

```typescript
// lib/api.ts — use this for all calls
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_KONG_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api
```

Kong routes:
```
POST /api/triage     → triage-agent
POST /api/sandbox    → code execution sandbox
POST /api/review     → code-review-agent
GET  /api/progress   → progress-agent
POST /api/exercises  → exercise-agent
GET  /api/alerts     → struggle alerts feed
```

---

## Authentication Flow

```
1. User submits login form
2. Better Auth validates credentials
3. JWT token returned and stored
4. Token attached to all Kong requests via axios interceptor
5. Kong validates JWT before forwarding to microservice
6. role field in JWT controls page access
```

Environment variables required:
```
NEXT_PUBLIC_KONG_URL=http://<kong-service-url>
NEXT_PUBLIC_AUTH_URL=http://<auth-service-url>
BETTER_AUTH_SECRET=<secret>
```

---

## TDD Rules — Non-Negotiable

```
1. Write the test file FIRST
2. Run tests → confirm they FAIL (red)
3. Write minimum implementation to make tests pass
4. Run tests → confirm they PASS (green)
5. Refactor if needed → tests must still pass
6. Commit with format:
   "Claude: red <component> tests"
   "Claude: green <component> passing"
```

Test file for every page and every component.
No exceptions.

---

## Testing Setup

```typescript
// jest.config.ts
import type { Config } from 'jest'
const config: Config = {
  testEnvironment: 'jsdom',
  setupFilesAfterFramework: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1'
  }
}
export default config

// jest.setup.ts
import '@testing-library/jest-dom'
```

Run tests:
```bash
cd frontend
npm test              # run all tests
npm test -- --watch   # watch mode
npm test -- --coverage # coverage report
```

---

## Coding Conventions

### Components
```typescript
// Always named exports
// Always TypeScript props interface
interface Props {
  studentName: string
  masteryScore: number
}

export function MasteryBar({ studentName, masteryScore }: Props) {
  // Tailwind only — no inline styles
  // shadcn/ui for UI primitives
}
```

### API Calls
```typescript
// Always use the api.ts instance
// Always handle errors
// Never hardcode URLs
import api from '@/lib/api'

const response = await api.post('/api/triage', {
  query: message,
  student_id: user.id
})
```

### Types
```typescript
// All types in types/ folder
// No `any` types — ever
export interface Student {
  id: string
  name: string
  email: string
  role: 'student' | 'teacher'
}
```

---

## Deployment

Use the `nextjs-k8s-deploy` skill only. Never deploy manually.

```bash
# From monorepo root
bash .claude/skills/nextjs-k8s-deploy/scripts/build.sh ./frontend
bash .claude/skills/nextjs-k8s-deploy/scripts/load_image.sh
bash .claude/skills/nextjs-k8s-deploy/scripts/deploy.sh
python .claude/skills/nextjs-k8s-deploy/scripts/get_url.py
```

---

## DO and DON'T

| ✅ DO | ❌ DON'T |
|---|---|
| Write tests before components | Write components without tests |
| Use `app/` router always | Use `pages/` router |
| Use shadcn/ui for UI primitives | Build UI components from scratch |
| Call all APIs through Kong | Call microservices directly |
| Use TypeScript interfaces for all props | Use `any` type |
| Use Tailwind classes only | Write inline styles |
| Use `api.ts` for all HTTP calls | Use `fetch` directly |
| Check `role` before showing teacher page | Assume all users are students |