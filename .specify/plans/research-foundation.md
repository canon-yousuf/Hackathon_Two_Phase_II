# Research: Foundation — Database Schema + Authentication Setup

**Date**: 2026-02-08

## R1: Better Auth JWT Plugin API

**Decision**: Use `jwt()` server plugin + `jwtClient()` client plugin
**Rationale**: Better Auth's JWT plugin is designed for cross-service auth — exactly our use case (Next.js issues tokens, FastAPI verifies them).

**Key Findings**:
- Server import: `import { jwt } from "better-auth/plugins"`
- Client import: `import { jwtClient } from "better-auth/plugins/client"` (NOT `"better-auth/client/plugins"`)
- Token retrieval: `authClient.token()` returns `{ data: { token: string }, error? }` (NOT `getToken()`)
- Route handler: `toNextJsHandler(auth.handler)` — note `.handler` property
- Algorithm: HS256 by default, matching PyJWT
- JWKS endpoint available at `/api/auth/jwks` but we use shared secret instead (simpler for hackathon)

**Alternatives Considered**:
- Bearer plugin: Simpler but uses localStorage (violates constitution security standards)
- NextAuth: Replaced by Better Auth per project requirements

## R2: Neon PostgreSQL Connection from Node.js

**Decision**: Use `pg` Pool for Better Auth database connection
**Rationale**: Better Auth documentation directly supports `pg` Pool. Neon is wire-compatible with standard PostgreSQL.

**Key Findings**:
- `pg` Pool works with Neon when `?sslmode=require` is in the connection string
- For serverless deployments (Vercel Edge), may need `@neondatabase/serverless` — defer to deployment phase
- Better Auth auto-creates `user`, `session`, `account`, `verification` tables on first connection

**Alternatives Considered**:
- `@neondatabase/serverless`: Better for edge runtime but adds complexity; defer unless needed
- Drizzle adapter: Better Auth supports it but adds unnecessary dependency

## R3: SQLModel + Neon Connection from Python

**Decision**: Use `create_engine` with `pool_pre_ping=True` and connection pooling
**Rationale**: Established pattern from database SKILL.md, handles Neon cold starts gracefully.

**Key Findings**:
- `pool_pre_ping=True` detects stale connections after Neon suspends (5 min idle)
- `pool_recycle=300` keeps connections fresh
- `psycopg2-binary` is the PostgreSQL driver for SQLModel/SQLAlchemy
- SSL is enforced by `?sslmode=require` in the connection string — no extra Python config needed

**Alternatives Considered**:
- `asyncpg` + async SQLAlchemy: More complex, SQLModel Session is sync anyway
- `psycopg[binary]` (v3): Newer but less ecosystem support with SQLModel

## R4: JWT Token Structure

**Decision**: Better Auth JWT contains `sub` (user ID), `email`, `name` claims
**Rationale**: Verified from auth spec FR-005 — token MUST contain user identifier, email, and name.

**Key Findings**:
- `sub` claim = Better Auth user ID (text, not integer)
- Backend decodes with `jwt.decode(token, SECRET, algorithms=["HS256"])`
- Token expiry default: 7 days (from auth spec FR-006)
- Backend reads `sub` and compares to URL `{user_id}` parameter

## R5: Table Coexistence

**Decision**: Better Auth tables (camelCase) and app tables (snake_case) coexist in same database
**Rationale**: Both connect to the same Neon database. Better Auth manages `user`, `session`, `account`. Backend manages `tasks`.

**Key Findings**:
- Better Auth column names: `emailVerified`, `createdAt`, `updatedAt` (camelCase)
- Tasks table column names: `user_id`, `created_at`, `updated_at` (snake_case)
- Foreign key: `tasks.user_id` → `user.id` — table name is `user` (singular, as Better Auth creates it)
- CASCADE delete: When Better Auth deletes a user, all their tasks are removed
- `SQLModel.metadata.create_all()` only creates tables defined in SQLModel — won't touch Better Auth tables
