# Tasks: Testing Strategy — Backend + Frontend Tests

**Input**: Design documents from `/specs/008-testing-strategy/` and `.specify/plans/plan-testing.md`
**Prerequisites**: plan-testing.md (required), spec.md (required for user stories)

**Tests**: YES — this entire feature IS the test suite. Every task produces test code.

**Organization**: Tasks are grouped by user story from the spec (US1–US7) to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/tests/` (pytest + httpx + SQLite)
- **Frontend**: `frontend/__tests__/` (Vitest + React Testing Library)

---

## Phase 1: Setup (Backend Test Infrastructure)

**Purpose**: Configure backend test dependencies, fixtures, and shared helpers so all backend test phases can proceed.

- [x] T001 Add `pytest-cov>=5.0.0` to dev dependencies in `backend/pyproject.toml`
- [x] T002 Create `backend/tests/conftest.py` with environment variable setup (DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS) at file scope BEFORE any app imports, SQLite in-memory engine, minimal `user` table for FK constraint, Session fixture with create_all/drop_all, mock JWT token helper (`create_test_token`), auth_headers helper, seed_test_user helper, AsyncClient fixture with get_session dependency override — per plan Phase 1
- [x] T003 Install backend dev dependencies by running `cd backend && uv pip install -e ".[dev]"` and verify `pytest --co` collects conftest without errors

**Checkpoint**: Backend test infrastructure ready — all fixtures importable, `pytest --co` succeeds

---

## Phase 2: Setup (Frontend Test Infrastructure)

**Purpose**: Configure frontend test runner, mocks, and shared setup so all frontend test phases can proceed.

**Note**: Phase 2 is independent of Phase 1 — backend and frontend setup can run in parallel.

- [x] T004 [P] Add test dependencies to `frontend/package.json` devDependencies: `vitest`, `@testing-library/react`, `@testing-library/jest-dom`, `@testing-library/user-event`, `@vitejs/plugin-react`, `jsdom` — and add scripts: `"test": "vitest run"`, `"test:watch": "vitest"`, `"test:coverage": "vitest run --coverage"`
- [x] T005 [P] Create `frontend/vitest.config.ts` with jsdom environment, react plugin, setup file reference, globals enabled, css disabled, `@` path alias to project root — per plan Phase 5.2
- [x] T006 [P] Create `frontend/vitest.setup.ts` with `import "@testing-library/jest-dom/vitest"` — per plan Phase 5.3
- [x] T007 Create `frontend/__mocks__/next/navigation.ts` with mocked `useRouter` (push, replace, back, refresh), `usePathname`, and `redirect` — per plan Phase 5.4
- [x] T008 Install frontend test dependencies by running `cd frontend && npm install` and verify `npx vitest run` executes (0 tests found, no errors)

**Checkpoint**: Frontend test infrastructure ready — `npx vitest run` succeeds with 0 tests, no config errors

---

## Phase 3: User Story 1 — Authentication Security Verification (Priority: P1)

**Goal**: Verify the backend auth middleware correctly rejects unauthorized requests (401) and user_id mismatches (403), and allows valid requests (200).

**Independent Test**: `cd backend && pytest tests/test_auth.py -v` — all 6 tests pass.

**FR Coverage**: FR-001 through FR-006

### Implementation

- [x] T009 [US1] Create `backend/tests/test_auth.py` with 6 async test functions using the AsyncClient fixture against GET `/api/{user_id}/tasks`:
  - `test_no_token_returns_401` (FR-001) — request with no Authorization header, assert status 401 or 403 (HTTPBearer may return 403)
  - `test_malformed_token_returns_401` (FR-002) — `Authorization: Bearer not-a-jwt`, assert 401
  - `test_expired_token_returns_401` (FR-003) — token with past expiry via `create_test_token(expired=True)`, assert 401
  - `test_wrong_secret_returns_401` (FR-004) — token signed with `wrong-secret-key-that-is-32-chars`, assert 401
  - `test_user_id_mismatch_returns_403` (FR-005) — valid token for TEST_USER_ID but URL uses OTHER_USER_ID, assert 403
  - `test_valid_token_matching_user_returns_200` (FR-006) — valid token + matching URL user_id, assert 200
- [x] T010 [US1] Run `cd backend && pytest tests/test_auth.py -v` and verify all 6 tests pass. If `test_no_token` returns 403 instead of 401, update the assertion to accept 403 (HTTPBearer default behavior) and add a comment explaining why.

**Checkpoint**: Auth middleware 100% covered (FR-070). Run: `pytest tests/test_auth.py --cov=app.middleware --cov-report=term-missing`

---

## Phase 4: User Story 2 — Task CRUD Operations Verification (Priority: P1)

**Goal**: Verify all 6 REST endpoints return correct status codes, response bodies, and enforce user isolation.

**Independent Test**: `cd backend && pytest tests/test_tasks.py -v` — all 32 tests pass.

**FR Coverage**: FR-007 through FR-038

### Implementation

- [x] T011 [US2] Create `backend/tests/test_tasks.py` with a `create_task_for_user` async helper function that POSTs to `/api/{user_id}/tasks` with auth_headers and returns the response JSON — used by all subsequent tests.

- [x] T012 [US2] Add GET list tests (9 tests) to `backend/tests/test_tasks.py`:
  - `test_list_tasks_empty` (FR-007) — no tasks exist, assert `[]`
  - `test_list_tasks_user_isolation` (FR-008) — create tasks for TEST_USER_ID and OTHER_USER_ID, list for TEST_USER_ID returns only their tasks
  - `test_list_tasks_filter_pending` (FR-009) — create pending + completed tasks, `?status=pending` returns only pending
  - `test_list_tasks_filter_completed` (FR-010) — `?status=completed` returns only completed
  - `test_list_tasks_filter_all` (FR-011) — `?status=all` returns all
  - `test_list_tasks_sort_created` (FR-012) — `?sort=created` returns newest first
  - `test_list_tasks_sort_title` (FR-013) — `?sort=title` returns alphabetical order
  - `test_list_tasks_invalid_status` (FR-014) — `?status=invalid` returns 422
  - `test_list_tasks_invalid_sort` (FR-015) — `?sort=invalid` returns 422

- [x] T013 [US2] Add POST create tests (7 tests) to `backend/tests/test_tasks.py`:
  - `test_create_task_valid_title` (FR-016) — `{"title": "Test"}` → 201
  - `test_create_task_with_description` (FR-017) — `{"title": "T", "description": "D"}` → 201 with description in response
  - `test_create_task_empty_title` (FR-018) — `{"title": ""}` → 422
  - `test_create_task_missing_title` (FR-019) — `{}` → 422
  - `test_create_task_title_too_long` (FR-020) — title of 201 chars → 422
  - `test_create_task_default_incomplete` (FR-021) — created task has `completed: false`
  - `test_create_task_correct_user_id` (FR-022) — created task has `user_id` == TEST_USER_ID

- [x] T014 [US2] Add GET single task tests (3 tests) to `backend/tests/test_tasks.py`:
  - `test_get_task_found` (FR-023) — create task, GET by id → 200 with matching data
  - `test_get_task_not_found` (FR-024) — GET non-existent id (99999) → 404
  - `test_get_task_other_user` (FR-025) — create task as OTHER_USER_ID, GET as TEST_USER_ID → 404

- [x] T015 [US2] Add PUT update tests (6 tests) to `backend/tests/test_tasks.py`:
  - `test_update_task_title_only` (FR-026) — `{"title": "New Title"}` → 200, title changed
  - `test_update_task_description_only` (FR-027) — `{"description": "New Desc"}` → 200, description changed
  - `test_update_task_both_fields` (FR-028) — both title and description → 200
  - `test_update_task_timestamp_changes` (FR-029) — `updated_at` in response differs from original
  - `test_update_task_not_found` (FR-030) — PUT non-existent id → 404
  - `test_update_task_empty_title` (FR-031) — `{"title": ""}` → 422

- [x] T016 [US2] Add DELETE tests (3 tests) to `backend/tests/test_tasks.py`:
  - `test_delete_task_success` (FR-032) — DELETE existing task → 204, no response body
  - `test_delete_task_not_found` (FR-033) — DELETE non-existent id → 404
  - `test_delete_task_no_longer_in_list` (FR-034) — after delete, GET list does not contain the task

- [x] T017 [US2] Add PATCH toggle completion tests (4 tests) to `backend/tests/test_tasks.py`:
  - `test_toggle_pending_to_completed` (FR-035) — new task (completed=false), toggle → completed=true
  - `test_toggle_completed_to_pending` (FR-036) — toggle twice → completed=false again
  - `test_toggle_timestamp_changes` (FR-037) — `updated_at` changes after toggle
  - `test_toggle_not_found` (FR-038) — PATCH non-existent id → 404

- [x] T018 [US2] Run `cd backend && pytest tests/test_tasks.py -v` and verify all 32 tests pass.

**Checkpoint**: CRUD endpoints fully tested. Run: `pytest tests/test_tasks.py --cov=app.routes --cov-report=term-missing` — target ≥ 90%

---

## Phase 5: User Story 5 — Service Layer Logic Verification (Priority: P1)

**Goal**: Unit test all service layer functions in isolation using direct Session calls (no HTTP).

**Independent Test**: `cd backend && pytest tests/test_service.py -v` — all 7 tests pass.

**FR Coverage**: FR-039 through FR-045

### Implementation

- [x] T019 [US5] Create `backend/tests/test_service.py` with 7 test functions using the Session fixture (NOT AsyncClient). Each test must call `seed_test_user(session)` before creating tasks. Import service functions from `app.services.task_service`:
  - `test_get_tasks_filters_by_user_id` (FR-039) — create tasks for 2 users via service, `get_tasks(session, user_a)` returns only user_a's
  - `test_get_tasks_filters_by_status` (FR-040) — create pending + completed tasks, `get_tasks(session, user, status="pending")` returns only pending
  - `test_get_tasks_sorts_correctly` (FR-041) — create tasks "B" then "A", `sort="title"` → A before B; `sort="created"` → newest first
  - `test_create_task_defaults` (FR-042) — `create_task(session, user_id, TaskCreate(title="X"))` returns task with `completed=False`, `created_at` and `updated_at` set
  - `test_update_task_partial` (FR-043) — create task, `update_task(session, user_id, task_id, TaskUpdate(title="New"), {"title"})` changes title but not description
  - `test_delete_task_returns_bool` (FR-044) — `delete_task(session, user_id, task_id)` returns `True`; `delete_task(session, user_id, 99999)` returns `False`
  - `test_toggle_complete_flips` (FR-045) — `toggle_complete` on pending → completed=True; toggle again → completed=False

- [x] T020 [US5] Run `cd backend && pytest tests/test_service.py -v` and verify all 7 tests pass. Run: `pytest tests/test_service.py --cov=app.services --cov-report=term-missing` — target ≥ 90%

**Checkpoint**: Service layer fully tested in isolation.

---

## Phase 6: User Story 6 — Frontend Component Rendering Verification (Priority: P2)

**Goal**: Verify all 5 UI components render correctly in various states and respond to user interactions.

**Independent Test**: `cd frontend && npx vitest run __tests__/components/` — all 16 tests pass.

**FR Coverage**: FR-046 through FR-061

### Implementation

- [x] T021 [P] [US6] Create `frontend/__tests__/components/TaskList.test.tsx` with 3 tests:
  - `renders task items when given tasks` (FR-046) — pass array of 3 mock tasks, verify 3 task titles appear in DOM
  - `renders empty state when no tasks` (FR-047) — pass empty array with `isLoading=false`, verify "No tasks yet" text
  - `renders loading skeletons when loading` (FR-048) — pass `isLoading=true`, verify 3 animated pulse elements rendered
  Mock strategy: import TaskList directly, pass mock callback functions, use `@testing-library/react` render + screen.

- [x] T022 [P] [US6] Create `frontend/__tests__/components/TaskItem.test.tsx` with 3 tests:
  - `displays title and completion status` (FR-049) — render with mock task, verify title text visible
  - `completed task has line-through` (FR-050) — render with `completed=true` task, verify `line-through` class on title element
  - `delete button triggers callback` (FR-051) — mock `window.confirm` to return true, click Delete button, verify `onDelete` called with task.id
  Mock strategy: import TaskItem directly, mock `window.confirm`.

- [x] T023 [P] [US6] Create `frontend/__tests__/components/TaskForm.test.tsx` with 4 tests:
  - `create mode shows empty fields and Add Task button` (FR-052) — render with `mode="create"`, verify inputs empty, button text "Add Task"
  - `edit mode shows prefilled fields and Update Task button` (FR-053) — render with `mode="edit"` and initialData, verify fields populated, button text "Update Task"
  - `empty title shows validation error` (FR-054) — clear title input, submit form, verify "Title is required" error text
  - `valid title triggers onSubmit` (FR-055) — type title, submit form, verify `onSubmit` called with `{title: "..."}` data
  Mock strategy: import TaskForm directly, use `@testing-library/user-event` for typing and submitting.

- [x] T024 [P] [US6] Create `frontend/__tests__/components/LoginForm.test.tsx` with 3 tests:
  - `renders email and password inputs` (FR-056) — verify both inputs present with correct types
  - `form submission calls signIn` (FR-057) — fill email + password, submit, verify `signIn(email, password)` called
  - `failed signin shows error message` (FR-058) — mock signIn to return `{ error: { message: "Invalid" } }`, verify error text displayed
  Mock strategy: mock `@/hooks/useAuth` module with `vi.mock`, mock `next/navigation` for useRouter.

- [x] T025 [P] [US6] Create `frontend/__tests__/components/SignupForm.test.tsx` with 3 tests:
  - `renders name, email, and password inputs` (FR-059) — verify all 3 inputs present
  - `form submission calls signUp` (FR-060) — fill all fields, submit, verify `signUp(email, password, name)` called
  - `duplicate email shows error message` (FR-061) — mock signUp to return `{ error: { message: "Email already exists" } }`, verify error text displayed
  Mock strategy: same as LoginForm — mock `@/hooks/useAuth` and `next/navigation`.

- [x] T026 [US6] Run `cd frontend && npx vitest run __tests__/components/ --reporter=verbose` and verify all 16 tests pass.

**Checkpoint**: All 5 components tested. Run: `npx vitest run --coverage` — components target ≥ 60%

---

## Phase 7: User Story 7 — Frontend API Client Verification (Priority: P2)

**Goal**: Verify the API client attaches JWT tokens and handles 401 redirects.

**Independent Test**: `cd frontend && npx vitest run __tests__/lib/` — all 2 tests pass.

**FR Coverage**: FR-062, FR-063

### Implementation

- [x] T027 [US7] Create `frontend/__tests__/lib/api.test.ts` with 2 tests:
  - `attaches Bearer token to outgoing requests` (FR-062) — mock `@/lib/auth-client` so `authClient.token()` returns `{ data: { token: "test-jwt" } }`, mock global `fetch` to return 200 with JSON body, call `api.getTasks("user-1")`, verify `fetch` was called with `Authorization: Bearer test-jwt` header
  - `redirects to login on 401 response` (FR-063) — mock `fetch` to return status 401, mock `window.location` with a writable `href`, call `api.getTasks("user-1")`, verify `window.location.href` was set to `/login`
  Mock strategy: `vi.mock("@/lib/auth-client")` for token control, `vi.stubGlobal("fetch", ...)` for network mock, `Object.defineProperty(window, "location", ...)` for redirect verification.

- [x] T028 [US7] Run `cd frontend && npx vitest run __tests__/lib/ --reporter=verbose` and verify both tests pass.

**Checkpoint**: API client tested. Run coverage to verify ≥ 80% on `lib/api.ts`.

---

## Phase 8: Polish & Cross-Cutting Verification

**Purpose**: Run full suites, verify coverage targets, confirm test independence.

- [x] T029 Run full backend test suite: `cd backend && pytest -v --cov=app --cov-report=term-missing` — verify:
  - All 45 tests pass (6 auth + 32 CRUD + 7 service)
  - `app/routes/tasks.py` coverage ≥ 90% (FR-068)
  - `app/services/task_service.py` coverage ≥ 90% (FR-069)
  - `app/middleware/auth.py` coverage = 100% (FR-070)
  - Suite completes in < 60 seconds (SC-008)

- [x] T030 Run full frontend test suite: `cd frontend && npm test` — verify:
  - All 18 tests pass (16 component + 2 API client)
  - Suite completes in < 30 seconds (SC-009)

- [x] T031 Run backend tests in random order to verify independence (FR-064): `cd backend && pytest -v -p randomly` (or `pytest -v` with no ordering dependency)

- [x] T032 Run frontend tests with coverage: `cd frontend && npx vitest run --coverage` — verify:
  - `components/` coverage ≥ 60% (FR-071)
  - `lib/api.ts` coverage ≥ 80% (FR-072)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Backend Setup)**: No dependencies — can start immediately
- **Phase 2 (Frontend Setup)**: No dependencies — can start immediately, **parallel with Phase 1**
- **Phase 3 (US1 Auth Tests)**: Depends on Phase 1
- **Phase 4 (US2 CRUD Tests)**: Depends on Phase 1
- **Phase 5 (US5 Service Tests)**: Depends on Phase 1
- **Phase 6 (US6 Component Tests)**: Depends on Phase 2
- **Phase 7 (US7 API Client Tests)**: Depends on Phase 2
- **Phase 8 (Polish)**: Depends on Phases 3–7 all complete

### User Story Dependencies

- **US1 (Auth)**: Independent — can start after Phase 1
- **US2 (CRUD)**: Independent — can start after Phase 1 (parallel with US1)
- **US3 (Validation)**: Covered within US2 tasks (FR-014, FR-015, FR-018–020, FR-031)
- **US4 (Filtering/Sorting)**: Covered within US2 tasks (FR-009–013)
- **US5 (Service Layer)**: Independent — can start after Phase 1 (parallel with US1, US2)
- **US6 (Frontend Components)**: Independent — can start after Phase 2 (parallel with backend phases)
- **US7 (API Client)**: Independent — can start after Phase 2 (parallel with US6)

### Within Each Phase

- Tasks within a phase are sequential unless marked [P]
- [P] tasks in Phase 6 (T021–T025) can all run in parallel (different files)
- Phase 2 tasks T004–T006 can run in parallel (different files)

### Parallel Opportunities

```text
Backend Setup (Phase 1)  ──┬── US1 Auth (Phase 3)   ───┐
                           ├── US2 CRUD (Phase 4)   ───┤
                           └── US5 Service (Phase 5) ───┤
                                                        ├── Phase 8 (Polish)
Frontend Setup (Phase 2) ──┬── US6 Components (Phase 6)┤
                           └── US7 API Client (Phase 7)─┘
```

---

## Parallel Example: Phase 6 (Component Tests)

```bash
# All 5 component test files can be written in parallel:
Task T021: "Create TaskList.test.tsx"    # different file
Task T022: "Create TaskItem.test.tsx"    # different file
Task T023: "Create TaskForm.test.tsx"    # different file
Task T024: "Create LoginForm.test.tsx"   # different file
Task T025: "Create SignupForm.test.tsx"  # different file
```

---

## Implementation Strategy

### MVP First (Backend Tests Only)

1. Complete Phase 1: Backend Setup (T001–T003)
2. Complete Phase 3: US1 Auth Tests (T009–T010)
3. Complete Phase 4: US2 CRUD Tests (T011–T018)
4. **STOP and VALIDATE**: `pytest -v` — all 38 backend tests pass
5. This alone provides 90%+ coverage on routes and 100% on auth

### Incremental Delivery

1. Phase 1 + Phase 2 → Setup ready (parallel)
2. Phase 3 (Auth) → Security verified
3. Phase 4 (CRUD) → Core functionality verified
4. Phase 5 (Service) → Business logic verified
5. Phase 6 (Components) → UI verified
6. Phase 7 (API Client) → Frontend-backend contract verified
7. Phase 8 (Polish) → Coverage validated, independence confirmed

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 32 |
| Phase 1 (Backend Setup) | 3 tasks |
| Phase 2 (Frontend Setup) | 5 tasks |
| Phase 3 (US1 Auth) | 2 tasks → 6 tests |
| Phase 4 (US2 CRUD) | 8 tasks → 32 tests |
| Phase 5 (US5 Service) | 2 tasks → 7 tests |
| Phase 6 (US6 Components) | 6 tasks → 16 tests |
| Phase 7 (US7 API Client) | 2 tasks → 2 tests |
| Phase 8 (Polish) | 4 tasks |
| **Total test cases** | **63 tests** |
| Parallel opportunities | 7 (Phase 1‖2, US1‖US2‖US5, US6‖US7, T021‖T022‖T023‖T024‖T025) |

## Notes

- US3 (Input Validation) and US4 (Filtering/Sorting) are covered within US2 CRUD tests — they share the same endpoint and test file
- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story phase is independently testable
- Commit after each phase completion
- FR-064 through FR-067 (cross-cutting) are enforced by conftest.py design (Phase 1)
- FR-068 through FR-072 (coverage) are validated in Phase 8
