---
id: "0002"
title: "Testing Implementation Plan"
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 008-testing-strategy
branch: 008-testing-strategy
user: human
command: /sp.plan
labels: [testing, plan, backend, frontend, pytest, vitest]
links:
  spec: specs/008-testing-strategy/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: .specify/plans/plan-testing.md
    action: created
tests:
  - none (plan only)
---

## Prompt

/sp.plan Save this plan at .specify/plans/plan-testing.md

Testing — Backend + Frontend Tests

Read these specs before planning:
- specs/testing/spec.md
- specs/api/spec.md
- specs/auth/spec.md
- specs/task-crud/spec.md
- specs/frontend-components/spec.md

Plan the implementation of the complete test suite. All features are already implemented.

1. Backend test setup — conftest.py with SQLite test engine, mock JWT helper, AsyncClient fixture, session dependency override
2. Backend auth tests (test_auth.py) — 6 scenarios from no-token to valid-token
3. Backend CRUD tests (test_tasks.py) — 32 tests covering GET list, POST, GET by id, PUT, DELETE, PATCH toggle
4. Backend service tests (test_service.py) — 7 unit tests for service layer functions
5. Frontend test setup — Vitest config, React Testing Library setup
6. Frontend component tests — TaskList, TaskItem, TaskForm, LoginForm, SignupForm
7. Frontend API client tests — JWT attachment, 401 redirect

Coverage targets: Backend routes/services 90%+, auth middleware 100%, frontend components 60%+

## Response snapshot

Created comprehensive implementation plan at `.specify/plans/plan-testing.md` covering 7 phases:
- Phase 1: Backend test setup (conftest.py with SQLite engine, mock JWT, AsyncClient fixture)
- Phase 2: Backend auth tests (6 tests, FR-001 to FR-006)
- Phase 3: Backend CRUD tests (32 tests, FR-007 to FR-038)
- Phase 4: Backend service unit tests (7 tests, FR-039 to FR-045)
- Phase 5: Frontend test setup (Vitest + RTL + mocks)
- Phase 6: Frontend component tests (16 tests, FR-046 to FR-061)
- Phase 7: Frontend API client tests (2 tests, FR-062 to FR-063)

Total: ~72 tests across backend and frontend. Identified 3 risks: SQLite/PG dialect differences, HTTPBearer 403 vs 401, module-level env var reads.

## Outcome

- Impact: Plan document created — ready for /sp.tasks or direct implementation
- Tests: N/A (plan phase — no code written)
- Files: 1 file created (.specify/plans/plan-testing.md)
- Next prompts: /sp.tasks to generate tasks.md, or /sp.implement to start coding
- Reflection: Thorough review of all source files before planning ensures accurate fixture design

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Implement Phase 1 (conftest.py) first to validate SQLite + env var approach
