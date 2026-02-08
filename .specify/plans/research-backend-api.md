# Research: Backend API — All 6 REST Endpoints + Service Layer

**Date**: 2026-02-08

## Research Questions & Findings

### RQ-1: What foundation code already exists?

**Decision**: Foundation is fully implemented and ready for the API layer.

**Evidence** (from code review):

| File | Status | Contents |
|------|--------|----------|
| `backend/app/main.py` | EXISTS | FastAPI app, CORS middleware, lifespan with `create_db_and_tables()`, health check at `/health` |
| `backend/app/config.py` | EXISTS | `Settings` dataclass with `DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`; `_require_env()` helper |
| `backend/app/db.py` | EXISTS | `engine` with `pool_pre_ping=True`, `get_session()` dependency, `create_db_and_tables()` |
| `backend/app/models/task.py` | EXISTS | `TaskBase`, `Task` (table), `TaskCreate`, `TaskUpdate`, `TaskResponse` schemas |
| `backend/app/middleware/auth.py` | EXISTS | `get_current_user()` (JWT verification), `enforce_user_access()` (user_id matching) |
| `backend/app/routes/__init__.py` | EXISTS | Empty |
| `backend/app/services/__init__.py` | EXISTS | Empty |

**No modifications needed** to foundation files (except `main.py` for router registration).

### RQ-2: How does the auth middleware work?

**Decision**: Use `get_current_user` as FastAPI `Depends()` on every route, then call `enforce_user_access()` manually.

**Rationale**:
- `get_current_user` extracts JWT from `Authorization: Bearer <token>` header
- Decodes with `HS256` using `BETTER_AUTH_SECRET` env var
- Returns `dict` with keys: `user_id` (from `sub` claim), `email`, `name`
- Raises 401 HTTPException for missing/expired/invalid tokens
- `enforce_user_access(user_id, current_user)` compares URL path `user_id` with token `user_id`
- Raises 403 HTTPException on mismatch

### RQ-3: How to handle partial updates (PUT with optional fields)?

**Decision**: Use Pydantic V2's `model_fields_set` to distinguish "field not sent" from "field sent as null".

**Rationale**:
- `TaskUpdate` has `title: Optional[str] = None` and `description: Optional[str] = None`
- If client sends `{"title": "New"}`, then `model_fields_set = {"title"}`
- If client sends `{"description": null}`, then `model_fields_set = {"description"}` and value is `None`
- If client sends `{}`, then `model_fields_set = set()` — reject with 422 (nothing to update)
- This correctly handles the spec requirement: "A field explicitly set to null MUST clear that field"

**Alternatives considered**:
- Using sentinel values (UNSET pattern): More complex, not needed for 2-field schema
- Accepting all fields as-is: Would not distinguish "not sent" from "sent as null"

### RQ-4: How to validate query parameters?

**Decision**: Use FastAPI `Query()` with `pattern` regex for `status` and `sort` params.

**Rationale**:
- `status: str = Query("all", alias="status", pattern="^(all|pending|completed)$")`
- `sort: str = Query("created", pattern="^(created|title)$")`
- FastAPI automatically returns 422 with descriptive error if pattern doesn't match
- No custom validation code needed

**Note on `alias`**: The `status` query param name conflicts with Python's `status` from `fastapi.status`. Use `status_filter` as the Python parameter name with `alias="status"` to expose it as `?status=` in the URL.

### RQ-5: SQLModel Session sync vs async?

**Decision**: Use synchronous `Session` with async route handlers. This is the established pattern.

**Rationale**:
- `get_session()` yields a sync `Session` via `with Session(engine)`
- FastAPI handles sync dependencies in async handlers by running them in a threadpool
- SQLModel does not officially support async sessions
- The existing `db.py` is already set up this way
- For hackathon scale (single-digit users), there is no performance concern

### RQ-6: How to handle the global exception handler?

**Decision**: Add a catch-all `Exception` handler in `main.py` that returns 500 with a generic JSON response.

**Rationale**:
- Prevents stack traces from leaking to clients
- Returns consistent JSON format: `{"detail": "Internal server error", "status_code": 500}`
- FastAPI's built-in `HTTPException` handler still takes precedence for 401/403/404/422
- `RequestValidationError` handler still takes precedence for Pydantic validation failures

## Summary

All research questions resolved. No NEEDS CLARIFICATION items remain. The implementation can proceed directly.
