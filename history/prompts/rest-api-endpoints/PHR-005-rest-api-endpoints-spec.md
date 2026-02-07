---
id: PHR-005
title: REST API Endpoints Specification
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: rest-api-endpoints
branch: 004-rest-api-endpoints
user: developer
command: /sp.specify
labels: [spec, api, rest, endpoints, crud]
links:
  spec: specs/004-rest-api-endpoints/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/004-rest-api-endpoints/spec.md
    action: created
    description: REST API endpoints spec with 8 user stories, 35 functional requirements, 10 success criteria
  - path: specs/004-rest-api-endpoints/checklists/requirements.md
    action: created
    description: Specification quality checklist — all items passing
tests:
  - N/A (specification document, no code tests)
---

## Prompt

/sp.specify REST API Endpoints for Phase II Todo Full-Stack Web Application

Defines exactly 6 RESTful endpoints under /api/{user_id}/tasks: list (with status/sort filters), create, get by id, update, delete, toggle completion. Includes request/response shapes, query parameters, validation rules, error responses, and cross-cutting auth requirements.

## Response snapshot

Created REST API endpoints specification on branch `004-rest-api-endpoints`:

- **Branch**: `004-rest-api-endpoints`
- **Spec file**: `specs/004-rest-api-endpoints/spec.md`
- **8 User Stories**: List tasks (P1), Create task (P1), View single task (P1), Update task (P1), Delete task (P1), Toggle completion (P1), Reject unauthorized (P1), Validate input (P2)
- **35 Functional Requirements**: FR-001 through FR-035 organized by endpoint (List: 8, Create: 6, Get: 2, Update: 6, Delete: 3, Toggle: 4, Cross-cutting: 6)
- **4 Key Entities**: Task response, Task Create request, Task Update request, Error response
- **8 Edge Cases**: boundary values (1 char, 200 chars, 1000 chars), partial updates, null clearing, invalid ID type, concurrent creation, combined filters
- **10 Success Criteria**: SC-001 through SC-010
- **0 NEEDS CLARIFICATION markers**
- **Quality checklist**: All items passing

Also committed and pushed the previous 3 specs (architecture, database, auth) on branch 003-auth-system.

## Outcome

- Impact: Defined the complete API contract for all 6 task endpoints with every success and error case specified
- Tests: N/A (specification)
- Files: specs/004-rest-api-endpoints/spec.md, specs/004-rest-api-endpoints/checklists/requirements.md
- Next prompts: /sp.specify for frontend pages spec, or /sp.plan for API implementation planning
- Reflection: Most detailed spec so far — 35 FRs grouped by endpoint make it easy for Backend Agent to implement one endpoint at a time

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist PASS — all items verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
