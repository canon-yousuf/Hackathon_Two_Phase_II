# Tasks: Foundation — Database Schema + Authentication Setup

**Input**: Design documents from `.specify/plans/plan-foundation.md`
**Prerequisites**: plan-foundation.md, specs 001-system-architecture, 002-database-schema, 003-auth-system, research-foundation.md, data-model-foundation.md
**Tests**: Not included — deferred to testing strategy feature

**Organization**: Tasks grouped by user story mapped from architecture, database, and auth specs.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1=Backend starts, US2=Auth works, US3=JWT verified)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project scaffolding — create directories, install dependencies, configure environment

- [x] T001 Create backend project scaffold with `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/models/__init__.py`, `backend/app/routes/__init__.py`, `backend/app/services/__init__.py`, `backend/app/middleware/__init__.py`
- [x] T002 Create `backend/.env.example` with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS placeholders
- [x] T003 [P] Initialize frontend Next.js 16 project in `frontend/` with TypeScript, Tailwind CSS, App Router — run `npx create-next-app@latest` then `npm install better-auth pg`
- [x] T004 [P] Create `frontend/.env.example` with BETTER_AUTH_SECRET, DATABASE_URL, NEXT_PUBLIC_API_URL, NEXT_PUBLIC_BETTER_AUTH_URL placeholders
- [x] T005 [P] Update root `.gitignore` to include `.env`, `.env.local`, `frontend/.env.local`, `backend/.env`, `node_modules/`, `__pycache__/`, `*.pyc`, `.venv/`
- [x] T006 [P] Create root `.env.example` with combined reference for all environment variables
- [x] T007 Install backend dependencies — run `cd backend && uv sync`

**Agent**: Database Agent (T001-T002, T007), Frontend Agent (T003-T004), orchestrator (T005-T006)

**Checkpoint**: Both `backend/` and `frontend/` directories exist with dependencies installed. `uv sync` and `npm install` succeed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before user stories — config, database engine, models

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Implement settings module in `backend/app/config.py` — `Settings` dataclass reading DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS from env vars. Fail fast with `ValueError` if DATABASE_URL or BETTER_AUTH_SECRET is missing
- [x] T009 Implement Neon database connection in `backend/app/db.py` — `create_engine` with `pool_pre_ping=True`, `pool_size=5`, `max_overflow=10`, `pool_recycle=300`. Export `create_db_and_tables()` and `get_session()` dependency. Follow `.claude/skills/database/SKILL.md` Neon Connection Setup
- [x] T010 Implement Task SQLModel models in `backend/app/models/task.py` — TaskBase (title 1-200 chars, description optional max 1000), Task table (id PK auto-increment, user_id FK→user.id with CASCADE indexed, completed bool default False indexed, created_at/updated_at UTC timestamps), TaskCreate, TaskUpdate (all optional), TaskResponse. Follow `.claude/skills/database/SKILL.md` SQLModel Definitions

**Agent**: Database Agent (T008-T010)

**Checkpoint**: Foundation ready — `from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse` imports without error. `create_db_and_tables()` creates `tasks` table in Neon.

---

## Phase 3: User Story 1 — Backend Starts and Serves Health Check (Priority: P1) MVP

**Goal**: Backend FastAPI application starts, creates tables on startup, serves `/health`, and has CORS configured

**Independent Test**: `uvicorn app.main:app --port 8000` starts → `GET /health` returns `{"status": "healthy"}` → `tasks` table exists in Neon

### Implementation for User Story 1

- [x] T011 [US1] Implement FastAPI app entry point in `backend/app/main.py` — asynccontextmanager lifespan calling `create_db_and_tables()`, CORSMiddleware reading CORS_ORIGINS from env (split by comma), health check endpoint `GET /health` returning `{"status": "healthy"}`, load .env via python-dotenv. Follow `.claude/skills/backend/SKILL.md` App Entry Point
- [x] T012 [US1] Verify backend starts — run `cd backend && uvicorn app.main:app --port 8000` and confirm health check returns 200

**Agent**: Backend Agent (T011), orchestrator (T012)

**Checkpoint**: Backend is running. `GET http://localhost:8000/health` returns 200. `tasks` table created in Neon.

---

## Phase 4: User Story 2 — Better Auth Registers and Authenticates Users (Priority: P1)

**Goal**: Frontend Better Auth setup complete — users can sign up, sign in, and obtain JWT tokens

**Independent Test**: `POST /api/auth/sign-up/email` with `{email, password, name}` creates user → `POST /api/auth/sign-in/email` returns session → `authClient.token()` returns a JWT string

### Implementation for User Story 2

- [x] T013 [US2] Implement Better Auth server config in `frontend/lib/auth.ts` — `betterAuth()` with `pg` Pool (connectionString from DATABASE_URL), `jwt()` plugin, `emailAndPassword: { enabled: true }`, secret from BETTER_AUTH_SECRET. Follow `.claude/skills/auth/SKILL.md` section 2
- [x] T014 [US2] Implement Better Auth API route handler in `frontend/app/api/auth/[...all]/route.ts` — export GET and POST via `toNextJsHandler(auth.handler)`. Follow `.claude/skills/auth/SKILL.md` section 3
- [x] T015 [P] [US2] Implement Better Auth client in `frontend/lib/auth-client.ts` — `createAuthClient` from `better-auth/react` with `jwtClient()` from `better-auth/plugins/client`, baseURL from NEXT_PUBLIC_BETTER_AUTH_URL. Follow `.claude/skills/auth/SKILL.md` section 4
- [x] T016 [US2] Implement auth hook in `frontend/hooks/useAuth.ts` — `"use client"` directive, useSession(), signUp (email, password, name), signIn (email, password), signOut, getToken (via `authClient.token()`). Follow `.claude/skills/auth/SKILL.md` section 5
- [x] T017 [US2] Verify auth flow — start frontend (`npm run dev`), `POST /api/auth/sign-up/email` creates user, `POST /api/auth/sign-in/email` returns session, user/session/account tables exist in Neon

**Agent**: Auth Agent (T013-T016), orchestrator (T017)

**Checkpoint**: Users can register and login via Better Auth. JWT tokens are issued. Auth tables auto-created in Neon.

---

## Phase 5: User Story 3 — Backend Verifies JWT and Enforces User Access (Priority: P1)

**Goal**: Backend JWT middleware verifies tokens signed by Better Auth and enforces user_id matching

**Independent Test**: Create a JWT with `sub=test-user`, send to backend with correct user_id → accepted. Send with wrong user_id → 403. Send expired token → 401. Send no token → 401.

### Implementation for User Story 3

- [x] T018 [US3] Implement JWT verification middleware in `backend/app/middleware/auth.py` — HTTPBearer security scheme, `get_current_user()` decoding JWT with PyJWT HS256 using BETTER_AUTH_SECRET, extracting sub/email/name, raising 401 for expired/invalid/missing-sub. `enforce_user_access()` comparing user_id with current_user, raising 403 on mismatch. Follow `.claude/skills/auth/SKILL.md` Backend Implementation section 2
- [x] T019 [US3] Verify JWT middleware — manually create a JWT signed with BETTER_AUTH_SECRET, test that `get_current_user()` decodes it correctly, test that expired tokens raise 401, test that `enforce_user_access()` raises 403 on mismatch

**Agent**: Auth Agent (T018), orchestrator (T019)

**Checkpoint**: JWT verification works end-to-end. Backend can verify tokens issued by frontend Better Auth using shared secret.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [x] T020 [P] Verify no `.env` files are committed — check `.gitignore` covers all env files
- [x] T021 [P] Verify database schema in Neon — `tasks` table has correct columns (id, user_id, title, description, completed, created_at, updated_at), indexes (user_id, completed, created_at), and FK constraint (user_id → user.id with CASCADE)
- [x] T022 End-to-end foundation verification — start backend (port 8000), start frontend (port 3000), sign up a user via Better Auth, obtain JWT token, verify backend can decode it with PyJWT, confirm all tables exist in Neon. Follow `.specify/plans/quickstart-foundation.md`

**Checkpoint**: Foundation is complete. All verification checklist items from `plan-foundation.md` pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on T001, T007 (backend scaffold + deps installed)
- **US1 Backend Starts (Phase 3)**: Depends on Phase 2 (config, db, models)
- **US2 Auth Works (Phase 4)**: Depends on T003 (frontend scaffold) — can run in PARALLEL with Phase 3
- **US3 JWT Verified (Phase 5)**: Depends on Phase 3 (backend running) + Phase 4 (tokens being issued)
- **Polish (Phase 6)**: Depends on all phases complete

### Parallel Opportunities

```
Phase 1:
  T001 (backend scaffold)  ←──── sequential ────→ T007 (uv sync)
  T003 (frontend scaffold) ──┐
  T004 (frontend .env)     ──┤── all parallel (different directories)
  T005 (.gitignore)        ──┤
  T006 (root .env.example) ──┘

Phase 2:
  T008 (config.py) ──┐
  T009 (db.py)     ──┤── T008+T009 parallel, then T010 (models depend on db)
  T010 (models)    ──┘

Phase 3 + Phase 4: CAN RUN IN PARALLEL
  Phase 3: T011 → T012 (backend)
  Phase 4: T013 → T014, T015 [P] → T016 → T017 (frontend)

Phase 5: REQUIRES both Phase 3 + Phase 4 complete
  T018 → T019
```

### Parallel Example: Setup Phase

```bash
# Launch these in parallel (different directories, no dependencies):
Agent: "T003 — Initialize frontend Next.js 16 project in frontend/"
Agent: "T005 — Update root .gitignore"
Agent: "T006 — Create root .env.example"
```

### Parallel Example: Phases 3 + 4

```bash
# Backend and frontend can be built simultaneously:
Backend Agent: "T011 — Implement FastAPI main.py"
Auth Agent: "T013 — Implement Better Auth server config"
# These touch different directories (backend/ vs frontend/)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1: Setup — scaffold both projects
2. Complete Phase 2: Foundational — config, db, models
3. Complete Phase 3: US1 — backend starts, health check works
4. **STOP and VALIDATE**: `GET /health` returns 200, `tasks` table exists
5. This alone proves the database layer works

### Incremental Delivery

1. Setup + Foundational → Project scaffolded, dependencies installed
2. US1 (Backend Starts) → Backend runs, tables created → Validate
3. US2 (Auth Works) → Users can register/login → Validate
4. US3 (JWT Verified) → Backend verifies frontend tokens → Validate
5. Each story adds capability without breaking previous stories

---

## Task Summary

| Phase | Tasks | Agent(s) |
|-------|-------|----------|
| Phase 1: Setup | T001-T007 (7 tasks) | Database, Frontend, orchestrator |
| Phase 2: Foundational | T008-T010 (3 tasks) | Database |
| Phase 3: US1 Backend Starts | T011-T012 (2 tasks) | Backend |
| Phase 4: US2 Auth Works | T013-T017 (5 tasks) | Auth |
| Phase 5: US3 JWT Verified | T018-T019 (2 tasks) | Auth |
| Phase 6: Polish | T020-T022 (3 tasks) | orchestrator |
| **Total** | **22 tasks** | |

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- No tests generated — deferred to testing strategy feature (spec 008)
- All code follows patterns from SKILL.md files
- Commit after each phase completion
- Stop at any checkpoint to validate independently
