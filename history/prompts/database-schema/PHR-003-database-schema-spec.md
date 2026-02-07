---
id: PHR-003
title: Database Schema Specification
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: database-schema
branch: 002-database-schema
user: developer
command: /sp.specify
labels: [spec, database, schema, neon, sqlmodel]
links:
  spec: specs/002-database-schema/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - path: specs/002-database-schema/spec.md
    action: created
    description: Database schema specification with 6 user stories, 19 functional requirements, 10 success criteria
  - path: specs/002-database-schema/checklists/requirements.md
    action: created
    description: Specification quality checklist — all items passing
tests:
  - N/A (specification document, no code tests)
---

## Prompt

/sp.specify Database Schema for Phase II Todo Full-Stack Web Application

Defines WHAT data the system stores — tables, columns, types, constraints, relationships, and indexes. Covers task entity with 7 columns (id, user_id, title, description, completed, created_at, updated_at), foreign key to user table with cascade delete, 3 indexes (user_id, completed, created_at), separate Pydantic schemas, Neon SSL connections, and cold start handling.

## Response snapshot

Created database schema specification on branch `002-database-schema`:

- **Branch**: `002-database-schema`
- **Spec file**: `specs/002-database-schema/spec.md`
- **6 User Stories**: Data persistence (P1), user isolation (P1), task lifecycle CRUD (P1), cascade delete (P2), efficient queries (P2), secure connections (P3)
- **19 Functional Requirements**: FR-001 through FR-019 covering task attributes, validation, referential integrity, cascade delete, user-scoped queries, indexes, SSL, env vars, cold starts, separate data shapes, UTC timestamps
- **2 Key Entities**: Task (primary), User (referenced)
- **5 Edge Cases**: empty/long title, long description, invalid user reference, duplicate timestamps, connection loss
- **10 Success Criteria**: SC-001 through SC-010 — all measurable and technology-agnostic
- **0 NEEDS CLARIFICATION markers**
- **Quality checklist**: All items passing

## Outcome

- Impact: Defined the complete data layer contract for all agents to reference
- Tests: N/A (specification)
- Files: specs/002-database-schema/spec.md, specs/002-database-schema/checklists/requirements.md
- Next prompts: /sp.plan for database implementation planning, or additional specs (auth, API, frontend)
- Reflection: User provided exhaustive column-level detail; spec stays technology-agnostic while preserving all constraints

## Evaluation notes (flywheel)

- Failure modes observed: Initial Write tool call failed because file wasn't read first — recovered by reading then writing
- Graders run and results (PASS/FAIL): Quality checklist PASS — all items verified
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
