# Claude Code Rules — Phase II Todo Full-Stack Web Application

## Project Overview

**Project:** Panaversity Hackathon II Phase II — Todo Full-Stack Web Application
**Objective:** Transform a console-based todo application into a multi-user, full-stack web application with authentication, persistent storage, and RESTful API.
**Development Approach:** Agentic Dev Stack with Spec-Driven Development (SDD): spec → plan → tasks → implement
**Surface:** Project-level orchestration via Claude Code with specialized sub-agents

**Success Criteria:**
- All outputs follow user intent and hackathon requirements
- Work is delegated to the correct specialized agent
- Prompt History Records (PHRs) are created for every user prompt
- ADR suggestions surface for significant architectural decisions
- All changes are small, testable, and reference code precisely

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 16+ (App Router), TypeScript, Tailwind CSS |
| Authentication | Better Auth with JWT plugin |
| Backend API | Python FastAPI, Pydantic V2 |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Tooling | Claude Code + Spec-Kit Plus, uv (Python), npm (Node) |

---

## Monorepo Structure

```
Hackathon_Two_Phase_II/
├── frontend/                  # Next.js 16+ application
│   ├── app/                   # App Router pages and layouts
│   ├── components/            # Reusable UI components
│   ├── lib/                   # Auth client, API client, utilities
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript type definitions
│   └── .env.local             # Frontend environment variables
├── backend/                   # FastAPI application
│   ├── app/
│   │   ├── main.py            # App entry, CORS, lifespan
│   │   ├── config.py          # Settings from env vars
│   │   ├── db.py              # Neon engine + session dependency
│   │   ├── models/            # SQLModel table + schemas
│   │   ├── routes/            # Thin route handlers
│   │   ├── middleware/        # JWT auth verification
│   │   └── services/          # Business logic + DB queries
│   ├── tests/                 # pytest test suite
│   └── .env                   # Backend environment variables
├── specs/                     # Feature specifications (SDD)
│   ├── api/                   # API endpoint specs
│   ├── database/              # Schema specs
│   ├── features/              # Feature specs (auth, tasks, etc.)
│   └── ui/                    # UI/page specs
├── history/
│   ├── prompts/               # Prompt History Records
│   │   ├── constitution/
│   │   ├── general/
│   │   └── <feature-name>/
│   └── adr/                   # Architecture Decision Records
├── .claude/
│   ├── agents/                # Specialized sub-agent definitions
│   │   ├── frontend.md
│   │   ├── backend.md
│   │   ├── database.md
│   │   ├── auth.md
│   │   └── testing.md
│   └── skills/                # Domain skill files
│       ├── frontend/frontend-SKILL.md
│       ├── backend/backend-SKILL.md
│       ├── database/database-SKILL.md
│       └── auth/auth-SKILL.md
├── .specify/                  # Spec-Kit Plus templates and scripts
│   ├── memory/constitution.md
│   └── templates/
└── CLAUDE.md                  # This file — project orchestrator
```

---

## Agent Delegation Rules (CRITICAL)

When Claude receives a task, it MUST delegate to the correct specialized agent via the Task tool. **Do not implement directly** — always route to the appropriate agent.

### Routing Table

| Agent | Trigger | Domain |
|-------|---------|--------|
| **frontend** | Any work in `frontend/`, UI pages, components, layouts, Tailwind styling, API client integration, form handling | Next.js 16 App Router, TypeScript, Tailwind CSS, Better Auth client |
| **backend** | Any work in `backend/`, FastAPI routes, service layer, error handling, CORS, middleware | FastAPI, Pydantic, route handlers, request/response schemas |
| **database** | Schema design, SQLModel models, Neon connection, migrations, indexing, service layer DB queries | SQLModel, Neon PostgreSQL, query patterns, data integrity |
| **auth** | Better Auth setup, JWT config, signup/signin/signout, token verification, protected routes, security | Better Auth, JWT, PyJWT, session management, CORS for auth |
| **testing** | Writing/running tests for backend (pytest) or frontend (Jest/Vitest) | Test fixtures, mock JWT, test client, coverage |

### Delegation Decision Process

1. **Identify the domain** — Which layer does this work touch?
2. **Check for overlap** — If work spans multiple domains (e.g., "add a new task field"), delegate to each agent in dependency order: database → backend → frontend
3. **Proactive delegation** — When creating a backend endpoint, proactively consider launching the auth agent to secure it and the testing agent to test it
4. **Never bypass** — Even for small changes, route through the correct agent. The agent will read its SKILL.md and follow established patterns.

### Agent Skill File References

Each agent MUST read its skill file before doing any work:

| Agent | Skill File Path |
|-------|----------------|
| frontend | `.claude/skills/frontend/frontend-SKILL.md` |
| backend | `.claude/skills/backend/backend-SKILL.md` |
| database | `.claude/skills/database/database-SKILL.md` |
| auth | `.claude/skills/auth/auth-SKILL.md` |

---

## API Endpoints (Hackathon Requirements)

All endpoints are scoped to `{user_id}` and require JWT authentication.

| Method | Path | Status | Description |
|--------|------|--------|-------------|
| GET | `/api/{user_id}/tasks` | 200 | List tasks (filter by `status`, sort by `created`/`title`) |
| POST | `/api/{user_id}/tasks` | 201 | Create a new task |
| GET | `/api/{user_id}/tasks/{id}` | 200 | Get a single task |
| PUT | `/api/{user_id}/tasks/{id}` | 200 | Update a task |
| DELETE | `/api/{user_id}/tasks/{id}` | 204 | Delete a task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | 200 | Toggle task completion |

---

## Environment Variables

### Frontend (`frontend/.env.local`)
```
BETTER_AUTH_SECRET=<shared-secret-min-32-chars>
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_db?sslmode=require
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### Backend (`backend/.env`)
```
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_db?sslmode=require
BETTER_AUTH_SECRET=<same-shared-secret-as-frontend>
CORS_ORIGINS=http://localhost:3000
```

**Rules:** Never hardcode secrets. Never commit `.env` files. Always provide `.env.example` with placeholder values.

---

## Spec-Driven Development Workflow

### Core Guarantees
- Record every user input verbatim in a PHR after every user message
- PHR routing (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/`
  - General → `history/prompts/general/`
- ADR suggestions: when an architecturally significant decision is detected, suggest: "📋 Architectural decision detected: <brief>. Document? Run `/sp.adr <title>`." Never auto-create ADRs; require user consent.

### PHR Creation Process

After completing requests, create a PHR:

1. **Detect stage** — One of: constitution | spec | plan | tasks | red | green | refactor | explainer | misc | general
2. **Generate title** — 3-7 words; create a slug for the filename
3. **Resolve route** — Constitution → `history/prompts/constitution/`, Feature → `history/prompts/<feature-name>/`, General → `history/prompts/general/`
4. **Create PHR** — Read template from `.specify/templates/phr-template.prompt.md`, allocate ID, fill ALL placeholders (ID, TITLE, STAGE, DATE_ISO, SURFACE="agent", MODEL, FEATURE, BRANCH, USER, COMMAND, LABELS, LINKS, FILES_YAML, TESTS_YAML, PROMPT_TEXT, RESPONSE_TEXT), write file
5. **Validate** — No unresolved placeholders, title/stage/dates match, PROMPT_TEXT complete, file exists at expected path
6. **Report** — Print ID, path, stage, title. On failure: warn but don't block.

### ADR Suggestions

Test for significance after design/architecture work:
- **Impact:** Long-term consequences? (framework, data model, API, security, platform)
- **Alternatives:** Multiple viable options considered?
- **Scope:** Cross-cutting and influences system design?

If ALL true, suggest: "📋 Architectural decision detected: [brief]. Document? Run `/sp.adr [title]`"

---

## Development Guidelines

### Authoritative Source Mandate
Agents MUST use MCP tools and CLI commands for information gathering. NEVER assume from internal knowledge; verify externally.

### Human as Tool Strategy
Invoke the user when:
1. **Ambiguous Requirements** — Ask 2-3 targeted clarifying questions
2. **Unforeseen Dependencies** — Surface and ask for prioritization
3. **Architectural Uncertainty** — Present options with tradeoffs
4. **Completion Checkpoint** — Summarize and confirm next steps

### Default Policies
- Clarify and plan first — keep business understanding separate from technical plan
- Do not invent APIs, data, or contracts; ask targeted clarifiers if missing
- Never hardcode secrets or tokens; use `.env` and docs
- Prefer the smallest viable diff; do not refactor unrelated code
- Cite existing code with code references (start:end:path)
- Keep reasoning private; output only decisions, artifacts, and justifications

### Execution Contract for Every Request
1. Confirm surface and success criteria (one sentence)
2. List constraints, invariants, non-goals
3. Produce the artifact with acceptance checks inlined
4. Add follow-ups and risks (max 3 bullets)
5. Create PHR in appropriate subdirectory under `history/prompts/`
6. If decisions meet ADR significance threshold, surface suggestion

### Minimum Acceptance Criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files where relevant

---

## Architect Guidelines (for planning)

When generating architectural plans, address:

1. **Scope and Dependencies** — In Scope, Out of Scope, External Dependencies
2. **Key Decisions and Rationale** — Options, Trade-offs, Principles
3. **Interfaces and API Contracts** — Inputs, Outputs, Errors, Error Taxonomy
4. **Non-Functional Requirements** — Performance, Reliability, Security, Cost
5. **Data Management** — Source of Truth, Schema Evolution, Migration, Rollback
6. **Operational Readiness** — Observability, Deployment, Feature Flags
7. **Risk Analysis** — Top 3 Risks, blast radius, guardrails
8. **Evaluation** — Definition of Done, Output Validation

---

## Code Standards

See `.specify/memory/constitution.md` for code quality, testing, performance, security, and architecture principles.

**Key rules:**
- Spec-driven: specs in `specs/` MUST exist before writing code
- Smallest viable diff — no unrelated edits
- Type safety everywhere (TypeScript strict mode, Python type hints)
- User isolation — every DB query MUST filter by user_id
- No hardcoded secrets — `.env` files only
- Thin route handlers — business logic in service layer
