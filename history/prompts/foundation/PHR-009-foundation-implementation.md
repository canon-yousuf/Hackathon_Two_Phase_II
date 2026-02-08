---
id: PHR-009
title: Foundation Layer Implementation
stage: green
date: 2026-02-08
surface: agent
model: claude-opus-4-6
feature: foundation
branch: 008-testing-strategy
user: developer
command: /sp.implement
labels: [implementation, database, auth, backend, frontend, foundation]
links:
  spec: specs/001-system-architecture/spec.md, specs/002-database-schema/spec.md, specs/003-auth-system/spec.md
  ticket:
  adr:
  pr:
files:
  - backend/pyproject.toml
  - backend/.env.example
  - backend/app/__init__.py
  - backend/app/config.py
  - backend/app/db.py
  - backend/app/main.py
  - backend/app/models/__init__.py
  - backend/app/models/task.py
  - backend/app/middleware/__init__.py
  - backend/app/middleware/auth.py
  - backend/app/routes/__init__.py
  - backend/app/services/__init__.py
  - backend/tests/__init__.py
  - frontend/lib/auth.ts
  - frontend/lib/auth-client.ts
  - frontend/app/api/auth/[...all]/route.ts
  - frontend/hooks/useAuth.ts
  - frontend/.env.example
  - .env.example
  - .gitignore
tests:
  - JWT middleware: valid token decodes correctly
  - JWT middleware: expired token raises 401
  - JWT middleware: invalid token raises 401
  - JWT middleware: wrong secret raises 401
  - JWT middleware: user mismatch raises 403
  - JWT middleware: matching user passes
  - TypeScript: frontend compiles with zero errors
  - Python: all backend modules import successfully
---

## Prompt

/sp.implement

Execute the foundation implementation plan from `.specify/plans/tasks-foundation.md` — 22 tasks across 6 phases covering backend scaffold, database layer, FastAPI entry point, Better Auth frontend setup, and JWT verification middleware.

## Response snapshot

Implemented all 22 tasks (T001-T022) across 6 phases. Key artifacts:

**Backend (7 files):**
- `config.py`: Settings dataclass with fail-fast validation
- `db.py`: Neon engine with pool_pre_ping, pool_size=5, pool_recycle=300
- `models/task.py`: TaskBase, Task (table), TaskCreate, TaskUpdate, TaskResponse with FK CASCADE
- `main.py`: FastAPI with lifespan, CORS, health check
- `middleware/auth.py`: get_current_user (PyJWT HS256), enforce_user_access (403 on mismatch)

**Frontend (4 files):**
- `lib/auth.ts`: Better Auth server with JWT plugin, pg Pool
- `lib/auth-client.ts`: Client with jwtClient from `better-auth/client/plugins`
- `app/api/auth/[...all]/route.ts`: API route handler
- `hooks/useAuth.ts`: signUp, signIn, signOut, getToken

**Fixes during implementation:**
1. SQLModel FK CASCADE syntax — used `sa_column=Column(String, ForeignKey(..., ondelete="CASCADE"))` instead of `sa_column_kwargs`
2. Better Auth import path — corrected from `better-auth/plugins/client` to `better-auth/client/plugins`
3. Added `@types/pg` dev dependency for TypeScript

**Verification:** All Python imports succeed, TypeScript compiles with 0 errors, JWT middleware passes 6 test scenarios.

## Outcome

- Impact: Foundation layer complete — backend starts, auth configured, JWT middleware ready
- Tests: 6 JWT middleware tests pass, TypeScript compilation clean
- Files: 20 files created/modified
- Next prompts: Configure real .env files with Neon credentials, then implement task CRUD endpoints
- Reflection: Background agents get blocked by plan mode — write files directly instead. Always verify TypeScript compilation to catch import path issues early.

## Evaluation notes (flywheel)

- Failure modes observed: (1) SQLModel sa_column_kwargs doesn't support ondelete, (2) research agent gave wrong Better Auth import path, (3) background agents can't write files in plan mode
- Graders run and results (PASS/FAIL): JWT middleware 6/6 PASS, TypeScript 0 errors PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Use direct file writes instead of background agents for implementation
