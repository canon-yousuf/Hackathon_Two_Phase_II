# Data Model: Backend API — All 6 REST Endpoints + Service Layer

**Date**: 2026-02-08

## Entities

All entities are already defined in `backend/app/models/task.py`. No new entities needed.

### Task (Database Table)

**Model**: `Task(TaskBase, table=True)` in `backend/app/models/task.py:15`
**Table name**: `tasks`

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | `Optional[int]` | Primary Key, auto-increment | Set by DB |
| `user_id` | `str` | FK → `user.id`, NOT NULL, indexed, CASCADE delete | Set by service layer |
| `title` | `str` | 1-200 chars, NOT NULL | Inherited from TaskBase |
| `description` | `Optional[str]` | max 1000 chars, nullable | Inherited from TaskBase |
| `completed` | `bool` | default `False`, indexed | Toggled by service |
| `created_at` | `datetime` | default `now(utc)` | Set once on creation |
| `updated_at` | `datetime` | default `now(utc)` | Manually refreshed on update/toggle |

**Indexes**:
- `user_id` — filter tasks by user (user isolation)
- `completed` — filter by completion status

### TaskCreate (Request Schema)

**Model**: `TaskCreate(TaskBase)` in `backend/app/models/task.py:38`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `title` | `str` | Yes | 1-200 characters |
| `description` | `Optional[str]` | No | max 1000 characters |

### TaskUpdate (Request Schema)

**Model**: `TaskUpdate(SQLModel)` in `backend/app/models/task.py:44`

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `title` | `Optional[str]` | No | 1-200 characters if provided |
| `description` | `Optional[str]` | No | max 1000 characters if provided |

**Business rule**: At least one field must be explicitly provided in the request body. If both are absent (empty `{}`), return 422.

### TaskResponse (Response Schema)

**Model**: `TaskResponse(TaskBase)` in `backend/app/models/task.py:51`

| Field | Type | Source |
|-------|------|--------|
| `id` | `int` | Task.id |
| `user_id` | `str` | Task.user_id |
| `title` | `str` | Task.title (inherited) |
| `description` | `Optional[str]` | Task.description (inherited) |
| `completed` | `bool` | Task.completed |
| `created_at` | `datetime` | Task.created_at |
| `updated_at` | `datetime` | Task.updated_at |

### ErrorResponse (New — for OpenAPI docs only)

| Field | Type | Description |
|-------|------|-------------|
| `detail` | `str` | Human-readable error message |
| `status_code` | `int` | HTTP status code |

**Note**: FastAPI's built-in HTTPException already returns `{"detail": "..."}`. The `status_code` field is added for frontend convenience. This schema is primarily for OpenAPI documentation.

## State Transitions

### Task Lifecycle

```
[Not Exists] --create--> [Incomplete] --toggle--> [Complete]
                              ^                       |
                              |---toggle--------------|
                              |
                         --update--> [Incomplete, modified]
                              |
                         --delete--> [Not Exists]
```

- **create**: title + optional description → `completed=false`, both timestamps set
- **update**: partial (title and/or description) → `updated_at` refreshed
- **toggle**: `completed` flipped → `updated_at` refreshed
- **delete**: permanent removal, no soft delete

## Validation Rules

| Rule | Enforced By | Error |
|------|-------------|-------|
| Title required (1-200 chars) | Pydantic `Field(min_length=1, max_length=200)` | 422 |
| Description max 1000 chars | Pydantic `Field(max_length=1000)` | 422 |
| Status query must be all/pending/completed | FastAPI `Query(pattern=...)` | 422 |
| Sort query must be created/title | FastAPI `Query(pattern=...)` | 422 |
| At least one field in update | Route handler check | 422 |
| Valid JWT required | `get_current_user` dependency | 401 |
| URL user_id matches token user_id | `enforce_user_access` | 403 |
| Task exists and belongs to user | Service layer query | 404 |
