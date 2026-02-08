# Tasks: Backend API — All 6 REST Endpoints + Service Layer

**Input**: Design documents from `.specify/plans/plan-backend-api.md`, `specs/004-rest-api-endpoints/spec.md`
**Prerequisites**: plan-backend-api.md (required), spec.md (required), research-backend-api.md, data-model-backend-api.md

**Tests**: Not included — testing has a separate spec (008-testing-strategy). Tests will be generated separately.

**Organization**: Tasks follow the plan's dependency order. Since this is a backend-only API layer building on existing foundation, user stories map to endpoint groups implemented together in the service + route layers.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US8 from API spec)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Foundation is already implemented. Verify existing code and confirm no changes needed.

- [ ] T001 Verify existing foundation files are intact: `backend/app/db.py`, `backend/app/config.py`, `backend/app/models/task.py`, `backend/app/middleware/auth.py`

**Checkpoint**: Foundation verified — service layer and routes can be built.

---

## Phase 2: Service Layer (Blocking Prerequisite for All Routes)

**Purpose**: Create all 6 service functions in a single file. Routes depend on these. All queries MUST filter by `user_id` for user isolation.

**Agent**: Database Agent with `.claude/skills/database/SKILL.md`

- [ ] T002 [P] Create `get_tasks()` and `get_task()` service functions in `backend/app/services/task_service.py`
  - `get_tasks(session: Session, user_id: str, status: str = "all", sort: str = "created") -> list[Task]`
    - `SELECT * FROM tasks WHERE user_id = ?`
    - If status == "pending": add `WHERE completed = False`
    - If status == "completed": add `WHERE completed = True`
    - If sort == "created": `ORDER BY created_at DESC`
    - If sort == "title": `ORDER BY title ASC`
    - Use `sqlmodel.select()` with `col()` for ordering
  - `get_task(session: Session, user_id: str, task_id: int) -> Task | None`
    - `SELECT * FROM tasks WHERE id = ? AND user_id = ?`
    - Return `None` if not found

- [ ] T003 [P] Create `create_task()` service function in `backend/app/services/task_service.py`
  - `create_task(session: Session, user_id: str, data: TaskCreate) -> Task`
  - Instantiate `Task(user_id=user_id, title=data.title, description=data.description)`
  - `session.add(task)`, `session.commit()`, `session.refresh(task)`
  - Return the created task

- [ ] T004 [P] Create `update_task()` service function in `backend/app/services/task_service.py`
  - `update_task(session: Session, user_id: str, task_id: int, data: TaskUpdate, fields_set: set[str]) -> Task | None`
  - Call `get_task()` — return `None` if not found
  - Only update fields present in `fields_set` (from `data.model_fields_set`)
  - If `"title"` in fields_set: `task.title = data.title`
  - If `"description"` in fields_set: `task.description = data.description` (handles null clearing)
  - Set `task.updated_at = datetime.now(timezone.utc)`
  - `session.add(task)`, `session.commit()`, `session.refresh(task)`

- [ ] T005 [P] Create `delete_task()` service function in `backend/app/services/task_service.py`
  - `delete_task(session: Session, user_id: str, task_id: int) -> bool`
  - Call `get_task()` — return `False` if not found
  - `session.delete(task)`, `session.commit()`
  - Return `True`

- [ ] T006 [P] Create `toggle_complete()` service function in `backend/app/services/task_service.py`
  - `toggle_complete(session: Session, user_id: str, task_id: int) -> Task | None`
  - Call `get_task()` — return `None` if not found
  - `task.completed = not task.completed`
  - `task.updated_at = datetime.now(timezone.utc)`
  - `session.add(task)`, `session.commit()`, `session.refresh(task)`

**Note**: T002-T006 all write to the same file (`task_service.py`). While logically parallel, they must be written as a single file. The [P] marks indicate they have no inter-function dependencies. **In practice, implement T002-T006 together as a single agent task writing the complete file.**

**Checkpoint**: Service layer complete. All 6 functions exist with user isolation, type hints, and proper timestamp handling.

---

## Phase 3: User Story 1 — List Tasks Endpoint (Priority: P1) 🎯 MVP

**Goal**: Authenticated user can list their tasks with status filtering and sorting.

**Independent Test**: `curl "http://localhost:8000/api/{user_id}/tasks?status=pending&sort=title" -H "Authorization: Bearer <token>"` returns 200 with filtered, sorted task array.

### Implementation

- [ ] T007 [US1] Create route handler `list_tasks` in `backend/app/routes/tasks.py`
  - Create `router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])`
  - `@router.get("", response_model=list[TaskResponse])`
  - Parameters: `user_id: str`, `status_filter: str = Query("all", alias="status", pattern="^(all|pending|completed)$")`, `sort: str = Query("created", pattern="^(created|title)$")`, `session: Session = Depends(get_session)`, `current_user: dict = Depends(get_current_user)`
  - Call `enforce_user_access(user_id, current_user)`
  - Return `task_service.get_tasks(session, user_id, status=status_filter, sort=sort)`
  - Import from: `app.db.get_session`, `app.middleware.auth.{get_current_user, enforce_user_access}`, `app.models.task.TaskResponse`, `app.services.task_service`

**Checkpoint**: List endpoint works with filtering and sorting. Invalid query params return 422.

---

## Phase 4: User Story 2 — Create Task Endpoint (Priority: P1)

**Goal**: Authenticated user can create a new task with title and optional description.

**Independent Test**: `curl -X POST "http://localhost:8000/api/{user_id}/tasks" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title": "Test"}'` returns 201 with created task.

### Implementation

- [ ] T008 [US2] Add route handler `create_task` in `backend/app/routes/tasks.py`
  - `@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)`
  - Parameters: `user_id: str`, `data: TaskCreate`, `session`, `current_user`
  - Call `enforce_user_access`, return `task_service.create_task(session, user_id, data)`

**Checkpoint**: Create endpoint returns 201. Empty title returns 422. Title > 200 chars returns 422.

---

## Phase 5: User Story 3 — Get Single Task Endpoint (Priority: P1)

**Goal**: Authenticated user can view a specific task by ID.

**Independent Test**: Create a task, then `curl "http://localhost:8000/api/{user_id}/tasks/{id}" -H "Authorization: Bearer <token>"` returns 200.

### Implementation

- [ ] T009 [US3] Add route handler `get_task` in `backend/app/routes/tasks.py`
  - `@router.get("/{task_id}", response_model=TaskResponse)`
  - Parameters: `user_id: str`, `task_id: int`, `session`, `current_user`
  - Call `enforce_user_access`, call `task_service.get_task(session, user_id, task_id)`
  - If `None`: raise `HTTPException(status_code=404, detail="Task not found")`

**Checkpoint**: Get returns 200 for existing task. Returns 404 for non-existent task.

---

## Phase 6: User Story 4 — Update Task Endpoint (Priority: P1)

**Goal**: Authenticated user can update a task's title and/or description via PUT.

**Independent Test**: `curl -X PUT "http://localhost:8000/api/{user_id}/tasks/{id}" -H "Authorization: Bearer <token>" -H "Content-Type: application/json" -d '{"title": "Updated"}'` returns 200 with updated task and refreshed `updated_at`.

### Implementation

- [ ] T010 [US4] Add route handler `update_task` in `backend/app/routes/tasks.py`
  - `@router.put("/{task_id}", response_model=TaskResponse)`
  - Parameters: `user_id: str`, `task_id: int`, `data: TaskUpdate`, `session`, `current_user`
  - Call `enforce_user_access`
  - Validate: `if not data.model_fields_set: raise HTTPException(status_code=422, detail="At least one field must be provided")`
  - Call `task_service.update_task(session, user_id, task_id, data, data.model_fields_set)`
  - If `None`: raise `HTTPException(status_code=404, detail="Task not found")`

**Checkpoint**: Update works with partial fields. Empty body `{}` returns 422. `{"description": null}` clears description.

---

## Phase 7: User Story 5 — Delete Task Endpoint (Priority: P1)

**Goal**: Authenticated user can permanently delete a task.

**Independent Test**: `curl -X DELETE "http://localhost:8000/api/{user_id}/tasks/{id}" -H "Authorization: Bearer <token>"` returns 204 with no body.

### Implementation

- [ ] T011 [US5] Add route handler `delete_task` in `backend/app/routes/tasks.py`
  - `@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)`
  - Parameters: `user_id: str`, `task_id: int`, `session`, `current_user`
  - Call `enforce_user_access`, call `task_service.delete_task(session, user_id, task_id)`
  - If `False`: raise `HTTPException(status_code=404, detail="Task not found")`
  - Return `None` (204 no content)

**Checkpoint**: Delete returns 204. Subsequent GET returns 404. Non-existent task returns 404.

---

## Phase 8: User Story 6 — Toggle Completion Endpoint (Priority: P1)

**Goal**: Authenticated user can toggle a task between complete and incomplete.

**Independent Test**: Create task (completed=false), PATCH toggle (completed=true), PATCH again (completed=false).

### Implementation

- [ ] T012 [US6] Add route handler `toggle_complete` in `backend/app/routes/tasks.py`
  - `@router.patch("/{task_id}/complete", response_model=TaskResponse)`
  - Parameters: `user_id: str`, `task_id: int`, `session`, `current_user`
  - Call `enforce_user_access`, call `task_service.toggle_complete(session, user_id, task_id)`
  - If `None`: raise `HTTPException(status_code=404, detail="Task not found")`

**Checkpoint**: Toggle flips completed status. `updated_at` is refreshed. Non-existent task returns 404.

---

## Phase 9: App Wiring & Error Handling (Cross-Cutting)

**Purpose**: Register the router in the app and add global error handling. Covers US7 (auth rejection) and US8 (input validation) implicitly.

**Agent**: Backend Agent with `.claude/skills/backend/SKILL.md`

- [ ] T013 [US7] Register task router and add global exception handler in `backend/app/main.py`
  - Add import: `from app.routes.tasks import router as tasks_router`
  - Add import: `from fastapi import Request` and `from fastapi.responses import JSONResponse`
  - Add: `app.include_router(tasks_router)` after CORS middleware
  - Add global exception handler:
    ```python
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "status_code": 500},
        )
    ```
  - Preserve existing: health check, CORS middleware, lifespan

**Checkpoint**: All 6 endpoints accessible at `/api/{user_id}/tasks`. Swagger UI at `/docs` shows all endpoints. Unhandled errors return 500 JSON.

---

## Phase 10: Verification

**Purpose**: End-to-end verification using Swagger UI and curl commands.

- [ ] T014 Run quickstart verification from `.specify/plans/quickstart-backend-api.md`
  - Start server: `cd backend && uvicorn app.main:app --reload --port 8000`
  - Verify health check: `GET /health` → 200
  - Verify Swagger UI loads at `/docs`
  - Test all 6 endpoints with valid JWT
  - Test auth rejection: no token → 401, wrong user → 403
  - Test validation: empty title → 422, invalid status param → 422

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Verify Foundation) → no deps, start immediately
Phase 2 (Service Layer)     → depends on Phase 1
Phases 3-8 (Route Handlers) → depend on Phase 2 (service must exist)
Phase 9 (App Wiring)        → depends on Phases 3-8 (router must exist to import)
Phase 10 (Verification)     → depends on Phase 9
```

### Critical Path

```
T001 → T002-T006 (single file) → T007-T012 (single file) → T013 → T014
```

**In practice, this is 4 atomic implementation steps:**
1. Verify foundation (T001)
2. Write `task_service.py` (T002-T006 combined)
3. Write `tasks.py` routes (T007-T012 combined)
4. Wire `main.py` + verify (T013-T014)

### Parallel Opportunities

- T002-T006 are logically parallel but target the same file — combine into one agent call
- T007-T012 are logically parallel but target the same file — combine into one agent call
- The service layer (T002-T006) and route handlers (T007-T012) CANNOT be parallel because routes import services

### Recommended Agent Execution

| Step | Agent | Tasks | File |
|------|-------|-------|------|
| 1 | Database Agent | T002-T006 | `backend/app/services/task_service.py` |
| 2 | Backend Agent | T007-T012 | `backend/app/routes/tasks.py` |
| 3 | Backend Agent | T013 | `backend/app/main.py` |
| 4 | Manual | T014 | Verification via curl/Swagger |

---

## Implementation Strategy

### MVP First (List + Create)

1. Complete T001 (verify foundation)
2. Complete T002-T006 (full service layer)
3. Complete T007-T008 (list + create routes)
4. Wire in T013 (register router)
5. **STOP and VALIDATE**: Can create and list tasks via Swagger

### Full Delivery

1. Complete all service functions (T002-T006)
2. Complete all route handlers (T007-T012)
3. Wire and verify (T013-T014)
4. All 6 endpoints working with auth, validation, and error handling

---

## Summary

| Metric | Value |
|--------|-------|
| Total tasks | 14 |
| Files to create | 2 (`task_service.py`, `tasks.py`) |
| Files to modify | 1 (`main.py`) |
| Agent calls needed | 3 (Database Agent, Backend Agent x2) |
| User stories covered | US1-US8 (6 endpoints + auth + validation) |
| Parallel opportunities | Limited (same-file tasks must be combined) |
| MVP scope | T001-T008, T013 (list + create endpoints) |
