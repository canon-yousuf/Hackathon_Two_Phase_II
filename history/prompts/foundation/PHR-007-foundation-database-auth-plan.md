---
id: PHR-007
title: Foundation Database Auth Implementation Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: foundation
branch: 008-testing-strategy
user: developer
command: /sp.plan
labels: [database, auth, foundation, plan]
links:
  spec: specs/001-system-architecture/spec.md, specs/002-database-schema/spec.md, specs/003-auth-system/spec.md
  ticket:
  adr:
  pr:
files:
  - .specify/plans/plan-foundation.md
  - .specify/plans/research-foundation.md
  - .specify/plans/data-model-foundation.md
  - .specify/plans/quickstart-foundation.md
tests:
  - none (plan phase — no code written)
---

## Prompt

/sp.plan Foundation — Database Schema + Authentication Setup

Read these specs before planning:
- specs/architecture/spec.md
- specs/database/spec.md
- specs/auth/spec.md

Plan the implementation of the foundation layer for the project. This covers:

1. Neon Serverless PostgreSQL connection setup
   - Engine with SSL, pooling, cold-start handling
   - Session dependency for FastAPI
   - create_db_and_tables on app startup

2. SQLModel models
   - TaskBase, Task (table), TaskCreate, TaskUpdate, TaskResponse
   - Fields, types, constraints, indexes exactly as database spec defines

3. Better Auth setup on frontend
   - Auth server config with JWT plugin
   - Auth client with jwtClient plugin
   - API route handler at /api/auth/[...all]

4. JWT verification on backend
   - HTTPBearer middleware
   - get_current_user dependency
   - enforce_user_access helper

5. Environment variables
   - .env.example with all required variables
   - .gitignore includes .env

Use these agents and skills:
- Database Agent with .claude/skills/database/SKILL.md
- Auth Agent with .claude/skills/auth/SKILL.md

This plan must produce a working foundation where:
- Backend starts and creates tables in Neon
- Better Auth can register and login users
- JWT tokens are issued and verifiable by backend
- No task endpoints yet — just the foundation

## Response snapshot

Generated a comprehensive implementation plan at `.specify/plans/plan-foundation.md` covering 4 phases (10 tasks total):
- Phase 1: Backend database layer (5 tasks — scaffold, db.py, config, models, main.py)
- Phase 2: Backend JWT middleware (1 task — auth.py with get_current_user + enforce_user_access)
- Phase 3: Frontend auth setup (5 tasks — scaffold, auth server, API route, auth client, useAuth hook)
- Phase 4: Environment and git setup (2 tasks — .gitignore, .env.example)

Research resolved 5 unknowns including Better Auth API corrections (token() not getToken(), import path differences from SKILL.md). Data model documented Task entity with all fields, constraints, indexes, and relationship to Better Auth's user table. Quickstart guide covers end-to-end setup from clone to verification.

## Outcome

- ✅ Impact: Foundation plan ready for task generation and implementation
- 🧪 Tests: N/A — plan phase, no code written
- 📁 Files: 4 planning artifacts created
- 🔁 Next prompts: /sp.tasks to generate tasks.md, then /sp.implement to execute
- 🧠 Reflection: Better Auth API differs from SKILL.md in key areas (import paths, method names). Research phase caught these before implementation, preventing debugging time.

## Evaluation notes (flywheel)

- Failure modes observed: SKILL.md has outdated Better Auth client import path and method name
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Update SKILL.md auth file with corrected Better Auth API
