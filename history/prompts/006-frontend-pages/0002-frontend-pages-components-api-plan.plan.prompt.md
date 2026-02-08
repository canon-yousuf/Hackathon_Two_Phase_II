---
id: "0002"
title: "Frontend pages components API plan"
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 006-frontend-pages
branch: 008-testing-strategy
user: developer
command: /sp.plan
labels: [frontend, planning, api-client, components, pages]
links:
  spec: specs/006-frontend-pages/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - .specify/plans/plan-frontend.md
tests:
  - none (planning phase)
---

## Prompt

/sp.plan Save this plan at .specify/plans/plan-frontend.md

Frontend — Pages + Components + API Client

Read these specs before planning:
- specs/architecture/spec.md
- specs/auth/spec.md
- specs/frontend-pages/spec.md
- specs/frontend-components/spec.md
- specs/task-crud/spec.md

Plan the implementation of the complete Next.js 16+ frontend. Backend API is already implemented.

1. Project setup — Next.js 16+ with App Router, TypeScript, Tailwind CSS
2. Auth integration — lib/auth.ts, lib/auth-client.ts, hooks/useAuth.ts, app/api/auth/[...all]/route.ts
3. API client — lib/api.ts with fetchWithAuth and typed api object
4. Pages — /, /login, /signup, /dashboard (protected)
5. Components — TaskList, TaskItem, TaskForm, TaskFilter, LoginForm, SignupForm, Navbar
6. Protected route layout — dashboard/layout.tsx checks session

This plan must produce a working frontend where user can sign up, sign in, sign out, and perform full task CRUD with JWT-authenticated API calls.

## Response snapshot

Created comprehensive implementation plan at `.specify/plans/plan-frontend.md` with:
- **Phase 0 (Research)**: 5 research items resolved — token method, API client pattern, protected route pattern, 204 handling, type definitions
- **Phase 1 (Design)**: Data model (Task, filter types), API contract (6 endpoints), component tree, file structure (16 new/modified files)
- **Phase 2 (Tasks)**: 16 implementation tasks with clear dependencies, acceptance criteria, and agent assignments
- **Implementation order**: 4 parallel batches with dependency chain documented
- **Risk analysis**: 3 risks identified with mitigations

Existing foundation layer verified: auth.ts, auth-client.ts, useAuth.ts, auth route handler all already implemented.

## Outcome

- Impact: Planning artifact created for full frontend implementation (16 tasks, 7 components, 4 pages, API client)
- Tests: N/A (planning phase)
- Files: .specify/plans/plan-frontend.md
- Next prompts: /sp.tasks to generate tasks.md, then /sp.implement to execute
- Reflection: All 5 specs read and cross-referenced. Existing code verified. No unknowns remaining.

## Evaluation notes (flywheel)

- Failure modes observed: setup-plan.sh detected wrong feature (testing-strategy branch), worked around by reading specs directly
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
