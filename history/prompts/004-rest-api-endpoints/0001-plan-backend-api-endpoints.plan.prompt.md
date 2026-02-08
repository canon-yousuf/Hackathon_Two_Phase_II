---
id: "0001"
title: "Plan Backend API Endpoints"
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: 004-rest-api-endpoints
branch: 008-testing-strategy
user: developer
command: /sp.plan
labels: [backend, api, service-layer, routes, error-handling]
links:
  spec: specs/004-rest-api-endpoints/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: .specify/plans/plan-backend-api.md
    action: created
  - path: .specify/plans/research-backend-api.md
    action: verified
  - path: .specify/plans/data-model-backend-api.md
    action: verified
  - path: .specify/plans/quickstart-backend-api.md
    action: created
tests:
  - none (plan phase, no code written)
---

## Prompt

/sp.plan Save this plan at .specify/plans/plan-backend-api.md

Backend API — All 6 REST Endpoints + Service Layer

Read these specs before planning:
- specs/architecture/spec.md
- specs/api/spec.md
- specs/task-crud/spec.md
- specs/database/spec.md

Plan the implementation of the complete backend API layer. Foundation (DB + Auth) is already implemented.

1. Service layer (backend/app/services/task_service.py)
   - get_tasks with status filtering and sorting
   - get_task by id with user_id enforcement
   - create_task
   - update_task
   - delete_task
   - toggle_complete

2. Route handlers (backend/app/routes/tasks.py)
   - All 6 endpoints from API spec
   - Every route uses get_current_user dependency
   - Every route calls enforce_user_access
   - Thin handlers — validate, delegate to service, return response

3. Error handling
   - Standardized ErrorResponse schema
   - Global exception handler
   - Proper HTTP status codes (200, 201, 204, 401, 403, 404, 422)

4. App wiring
   - Register task router in main.py
   - CORS middleware configured
   - Health check endpoint

Use these agents and skills:
- Backend Agent with .claude/skills/backend/SKILL.md
- Database Agent with .claude/skills/database/SKILL.md (for service layer queries)

This plan must produce a working API where:
- All 6 endpoints respond correctly
- JWT auth enforced on every endpoint
- User isolation verified on every query
- Testable with curl or Swagger UI at /docs

## Response snapshot

Created comprehensive implementation plan for the backend API layer with 4 artifacts:

1. **plan-backend-api.md** — Main implementation plan covering service layer (6 functions), route handlers (6 endpoints), error handling, and app wiring. Includes constitution check (all PASS), dependency-ordered tasks, and risk analysis.

2. **research-backend-api.md** — Pre-existing, verified. Covers 6 research questions: foundation code inventory, auth middleware behavior, partial update strategy (model_fields_set), query param validation (regex patterns), sync Session with async handlers, and global exception handler approach.

3. **data-model-backend-api.md** — Pre-existing, verified. Documents all entities (Task, TaskCreate, TaskUpdate, TaskResponse, ErrorResponse), state transitions, validation rules, and query patterns.

4. **quickstart-backend-api.md** — Step-by-step verification guide with curl commands for all 6 endpoints plus error scenarios (401, 403, 422).

Key design decisions:
- Use `model_fields_set` for partial update semantics (distinguish omitted vs null)
- Use `Query(pattern=...)` for status/sort validation (auto 422)
- Route-level check for empty update body (simpler than model_validator)
- Global exception handler for 500s with consistent JSON format

## Outcome

- Impact: Plan artifacts ready for /sp.tasks generation, then implementation
- Tests: N/A (plan phase)
- Files: 2 created (plan, quickstart), 2 verified (research, data-model)
- Next prompts: /sp.tasks to generate atomic task list, then /sp.implement
- Reflection: Foundation layer was well-structured, making the plan straightforward. All unknowns resolved from code review — no external research needed.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
