# Tasks: Frontend — Pages + Components + API Client

**Input**: Design documents from `.specify/plans/plan-frontend.md`, `specs/006-frontend-pages/spec.md`, `specs/007-frontend-components/spec.md`
**Prerequisites**: plan-frontend.md (required), specs 001, 003, 005, 006, 007 (required)

**Tests**: Not included — testing is deferred to the testing strategy feature (008-testing-strategy).

**Organization**: Tasks grouped by user story. User stories consolidated from specs 006 (pages) and 007 (components) into functional user journeys.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1–US5)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/` directory (Next.js 16+ App Router)
- All component files: `frontend/components/`
- All library files: `frontend/lib/`
- All type files: `frontend/types/`
- All page files: `frontend/app/`

## User Story Map

| Story | Title | Priority | Specs |
|-------|-------|----------|-------|
| US1 | User Signs Up and Reaches Dashboard | P1 | 006-US1, 007-US6 |
| US2 | User Signs In and Views Dashboard | P1 | 006-US2, 006-US3, 007-US5 |
| US3 | User Creates, Edits, Deletes, and Toggles Tasks | P1 | 005-US1–US5, 007-US1–US3, 007-US8 |
| US4 | User Filters and Sorts Tasks | P2 | 005-US1 (filter/sort), 007-US4 |
| US5 | User Signs Out and Route Protection Works | P2 | 006-US4, 006-US6, 006-US7, 007-US7 |

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: TypeScript types and API client — foundational for all user stories

- [x] T001 [P] Create TypeScript type definitions in `frontend/types/task.ts` — define `Task`, `TaskCreateData`, `TaskUpdateData` interfaces and `StatusFilter`, `SortOption` type aliases matching backend `TaskResponse` schema exactly: `{ id: number, user_id: string, title: string, description: string | null, completed: boolean, created_at: string, updated_at: string }`
- [x] T002 Create API client module in `frontend/lib/api.ts` — implement `fetchWithAuth(path, options)` that gets JWT via `authClient.token()`, attaches `Authorization: Bearer <token>` header, handles 401 (redirect to /login), handles 204 No Content (return null, don't parse JSON), throws on non-OK with error detail. Create typed `api` object with methods: `getTasks(userId, status?, sort?)`, `getTask(userId, taskId)`, `createTask(userId, data)`, `updateTask(userId, taskId, data)`, `deleteTask(userId, taskId)`, `toggleComplete(userId, taskId)`. Import types from `@/types/task`. Base URL from `NEXT_PUBLIC_API_URL`.
- [x] T003 [P] Update root layout metadata in `frontend/app/layout.tsx` — change title from "Create Next App" to "Todo App" and description to "Full-stack todo application with task management"

**Checkpoint**: Types and API client ready — component and page implementation can begin.

---

## Phase 2: Foundational (Auth Pages + Protected Layout)

**Purpose**: Auth infrastructure that MUST be complete before dashboard features work

**CRITICAL**: Dashboard cannot function without auth pages and protected layout.

- [x] T004 [P] Create LoginForm component in `frontend/components/LoginForm.tsx` — `"use client"` with email input (type="email", required), password input (type="password", required), "Sign In" submit button. Loading state: button disabled + "Signing in..." text. Error state: inline red error message below form. Link to /signup: "Don't have an account? Sign up". On success: `router.push("/dashboard")`. Uses `signIn(email, password)` from `useAuth()`. Prevents double submission.
- [x] T005 [P] Create SignupForm component in `frontend/components/SignupForm.tsx` — `"use client"` with name input (required), email input (type="email", required), password input (type="password", required, minLength=8 validated client-side). "Sign Up" submit button. Loading state: button disabled + "Creating account..." text. Error state: inline error (duplicate email, validation). Link to /login: "Already have an account? Sign in". On success: `router.push("/dashboard")`. Uses `signUp(email, password, name)` from `useAuth()`. Prevents double submission.
- [x] T006 [P] Create Navbar component in `frontend/components/Navbar.tsx` — `"use client"` displaying user's name or email from `useAuth().session`. App title "Todo App" on left. "Sign Out" button on right. On signout: calls `signOut()` then `router.push("/login")`. Tailwind: sticky top-0, white bg, shadow, flex justify-between, items-center, px-6, py-3.
- [x] T007 [P] Create dashboard protected layout in `frontend/app/dashboard/layout.tsx` — `"use client"` layout that checks auth via `useAuth()`. If `isLoading`, show centered spinner. If `!isAuthenticated`, redirect to /login via `router.push("/login")`. If authenticated, render `{children}`. Uses `useEffect` for redirect.
- [x] T008 [P] Create login page in `frontend/app/login/page.tsx` — `"use client"` page rendering LoginForm centered. Check `useAuth()` — if already authenticated, redirect to /dashboard. Centered layout: min-h-screen, flex items-center justify-center, bg-gray-50. App title "Todo App" above form.
- [x] T009 [P] Create signup page in `frontend/app/signup/page.tsx` — `"use client"` page rendering SignupForm centered. Check `useAuth()` — if already authenticated, redirect to /dashboard. Same centered layout as login page with "Todo App" title.

**Checkpoint**: Auth flow complete — user can sign up, sign in, see protected dashboard layout, and be redirected when unauthenticated.

---

## Phase 3: User Story 1 — User Signs Up and Reaches Dashboard (Priority: P1) — MVP

**Goal**: A new user can visit /signup, create an account, and land on /dashboard.

**Independent Test**: Navigate to /signup, fill in name + email + password, submit. Verify redirect to /dashboard with user's name in navbar.

### Implementation for User Story 1

> Note: All US1 tasks depend on Phase 2 (LoginForm, SignupForm, Navbar, dashboard layout, login/signup pages). These are already covered in Phase 2 since they're shared infrastructure. US1 specifically adds the dashboard page shell that the user lands on after signup.

- [x] T010 [US1] Create dashboard page shell in `frontend/app/dashboard/page.tsx` — `"use client"` page that imports and renders Navbar. Gets user session from `useAuth()`. For now, displays Navbar + a placeholder message "Welcome to your dashboard!". This establishes the post-signup landing page. Will be expanded in US3 with task components.

**Checkpoint**: US1 complete — new user can sign up, auto-login, see dashboard with their name in navbar.

---

## Phase 4: User Story 2 — User Signs In and Views Dashboard (Priority: P1)

**Goal**: A returning user can visit /login, sign in with credentials, and see their dashboard.

**Independent Test**: Create account via signup, sign out, navigate to /login, enter credentials, submit. Verify redirect to /dashboard.

### Implementation for User Story 2

> Note: US2 requires LoginForm (T004), login page (T008), and dashboard (T010) — all already created. US2 verifies the login flow works end-to-end. The root page redirect completes this story.

- [x] T011 [US2] Update root page redirect in `frontend/app/page.tsx` — `"use client"` component replacing default Next.js boilerplate. Uses `useAuth()` to check auth status. If `isLoading`: show centered spinner (animate-spin). If `isAuthenticated`: `router.replace("/dashboard")`. If not authenticated: `router.replace("/login")`. Minimal page — just the redirect logic.

**Checkpoint**: US2 complete — returning users can sign in and reach dashboard. Root URL redirects correctly.

---

## Phase 5: User Story 3 — User Creates, Edits, Deletes, and Toggles Tasks (Priority: P1)

**Goal**: Authenticated user can perform full CRUD on tasks: create, view, edit, delete, toggle completion. All data flows through the backend API with JWT.

**Independent Test**: Sign in, create a task "Buy groceries", verify it appears in the list. Edit title to "Buy organic groceries", verify update. Toggle completion, verify strikethrough. Delete with confirmation, verify removal.

### Implementation for User Story 3

- [x] T012 [P] [US3] Create TaskItem component in `frontend/components/TaskItem.tsx` — `"use client"` with props `{ task: Task, onToggle: (id: number) => void, onEdit: (task: Task) => void, onDelete: (id: number) => void }`. Display: title (strikethrough + text-gray-400 if completed, else text-gray-900), description (truncated to 150 chars with "..." if longer), completion checkbox (checked if completed), formatted creation date (use `new Date(task.created_at).toLocaleDateString()`). Completed tasks: line-through on title, muted colors, checkmark icon. Edit button (pencil/text). Delete button (red, calls `window.confirm("Delete this task?")` before `onDelete`). Per-item loading state via internal `isToggling`/`isDeleting` useState booleans — show spinner on checkbox during toggle, disable delete button during delete.
- [x] T013 [P] [US3] Create TaskForm component in `frontend/components/TaskForm.tsx` — `"use client"` with props `{ mode: "create" | "edit", initialData?: Task, onSubmit: (data: TaskCreateData | TaskUpdateData) => Promise<void>, onCancel?: () => void }`. Title input: required, maxLength=200, with char counter. Description textarea: optional, maxLength=1000, with char counter. Validation: if title empty on submit, show "Title is required" error inline. If title > 200 chars, show "Title must be 200 characters or less". Submit button: "Add Task" (create mode) / "Update Task" (edit mode). Cancel button: shown only in edit mode, calls `onCancel`. Loading state: button disabled + "Adding..." / "Updating..." text during submit. Error state: show error message above submit if `onSubmit` throws. On successful create: clear all fields. On successful edit: call `onCancel` to close edit mode. Preserve user input on error.
- [x] T014 [P] [US3] Create TaskList component in `frontend/components/TaskList.tsx` — `"use client"` with props `{ tasks: Task[], isLoading: boolean, error: string | null, onRetry: () => void, onToggle: (id: number) => void, onEdit: (task: Task) => void, onDelete: (id: number) => void }`. Four states: (1) Loading: 3 skeleton blocks using animate-pulse with h-20 bg-gray-200 rounded-lg. (2) Error: red error message + "Retry" button calling `onRetry`. (3) Empty: "No tasks yet. Create your first task!" centered message with muted styling. (4) Populated: renders TaskItem for each task in a flex flex-col gap-3 container. Import TaskItem from `@/components/TaskItem`.
- [x] T015 [US3] Expand dashboard page with full CRUD in `frontend/app/dashboard/page.tsx` — Replace US1 shell. `"use client"` page orchestrating all components. State: `tasks: Task[]`, `isLoading: boolean`, `error: string | null`, `statusFilter: StatusFilter` (default "all"), `sortOption: SortOption` (default "created"), `editingTask: Task | null`. On mount + when filter/sort changes: call `api.getTasks(userId, statusFilter, sortOption)`, set tasks/loading/error. Handler `handleCreate(data)`: call `api.createTask(userId, data)`, refetch tasks. Handler `handleUpdate(data)`: call `api.updateTask(userId, editingTask.id, data)`, refetch tasks, set editingTask=null. Handler `handleDelete(id)`: call `api.deleteTask(userId, id)`, refetch tasks. Handler `handleToggle(id)`: call `api.toggleComplete(userId, id)`, refetch tasks. Handler `handleEdit(task)`: set `editingTask = task`. Render layout: Navbar at top, then max-w-4xl mx-auto p-6 container with TaskForm (mode=editingTask ? "edit" : "create", initialData=editingTask, onSubmit/onCancel), TaskFilter (statusFilter, sortOption, onChange handlers), TaskList (tasks, isLoading, error, onRetry=refetch, onToggle, onEdit, onDelete). Get `userId` from `session.user.id`.

**Checkpoint**: US3 complete — full task CRUD working. User can create, view, edit, delete, and toggle tasks with loading/error/empty states.

---

## Phase 6: User Story 4 — User Filters and Sorts Tasks (Priority: P2)

**Goal**: User can filter tasks by status (all/pending/completed) and sort by creation date or title.

**Independent Test**: Create 3 tasks, complete 1. Select "Pending" filter — verify 2 tasks shown. Select "Completed" — verify 1 task. Select "Alphabetical" sort — verify order.

### Implementation for User Story 4

- [x] T016 [US4] Create TaskFilter component in `frontend/components/TaskFilter.tsx` — `"use client"` with props `{ statusFilter: StatusFilter, sortOption: SortOption, onStatusChange: (s: StatusFilter) => void, onSortChange: (s: SortOption) => void }`. Status filter: 3 buttons ("All", "Pending", "Completed"). Active button: bg-blue-600 text-white. Inactive: bg-gray-100 text-gray-700 hover:bg-gray-200. Button group with rounded-lg overflow-hidden, flex. Sort control: 2 buttons ("Newest First" for "created", "Alphabetical" for "title"). Same active/inactive styling. Flex wrap gap-4 between filter and sort groups. Import types from `@/types/task`.
- [x] T017 [US4] Integrate TaskFilter into dashboard page `frontend/app/dashboard/page.tsx` — Import TaskFilter. Add it between TaskForm and TaskList. Wire `statusFilter`/`sortOption` state and `onStatusChange`/`onSortChange` handlers. The `useEffect` that fetches tasks already has `statusFilter` and `sortOption` as dependencies (from T015), so changing filters triggers refetch automatically.

**Checkpoint**: US4 complete — filter and sort controls work, task list updates immediately on selection.

---

## Phase 7: User Story 5 — User Signs Out and Route Protection Works (Priority: P2)

**Goal**: Authenticated user can sign out. Unauthenticated users are redirected to login. Root URL routes correctly.

**Independent Test**: Sign in, click "Sign Out" in navbar. Verify redirect to /login. Try navigating to /dashboard directly — verify redirect to /login. Visit / — verify redirect to /login.

### Implementation for User Story 5

> Note: Navbar (T006) already has signout. Dashboard layout (T007) already has auth guard. Root page (T011) already has redirect. US5 adds the 404 page and verifies everything works together.

- [x] T018 [P] [US5] Create 404 page in `frontend/app/not-found.tsx` — Simple page: "Page not found" heading, "The page you're looking for doesn't exist." description, "Go to Dashboard" link to /dashboard. Centered layout, Tailwind styling.

**Checkpoint**: US5 complete — signout, route protection, root redirect, and 404 all functional.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements across all stories

- [x] T019 Verify all pages compile without TypeScript errors — run `cd frontend && npx tsc --noEmit` and fix any type errors across all created files
- [x] T020 Verify frontend builds successfully — run `cd frontend && npm run build` and fix any build errors

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on T001 (types for imports) and T002 (API client)
  - T004–T006 (components) can start as soon as T001 is done (they only need types indirectly via useAuth)
  - T007–T009 (pages) can start in parallel with components
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 2 completion (can run parallel with US1)
- **Phase 5 (US3)**: Depends on T002 (API client) and Phase 2 (dashboard layout)
- **Phase 6 (US4)**: Depends on T015 (dashboard page with CRUD)
- **Phase 7 (US5)**: Depends on Phase 2 (can run parallel with US3/US4)
- **Phase 8 (Polish)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (Sign Up)**: Phase 2 → T010
- **US2 (Sign In)**: Phase 2 → T011 (can parallel with US1)
- **US3 (Task CRUD)**: T001 + T002 → T012, T013, T014 (parallel) → T015
- **US4 (Filter/Sort)**: T015 → T016 → T017
- **US5 (Sign Out/Protection)**: Phase 2 → T018 (can parallel with US1–US4)

### Within Each User Story

- Types before API client
- Components before pages that use them
- Individual components can be built in parallel (different files)
- Dashboard page (T015) is the integration point — depends on all components

### Parallel Opportunities

Tasks that can run simultaneously (different files, no shared dependencies):

```
Batch 1: T001, T003 (types + layout metadata)
Batch 2: T002 (API client — needs T001)
Batch 3: T004, T005, T006, T007, T008, T009 (all components + pages — parallel)
Batch 4: T010, T011, T012, T013, T014, T016, T018 (dashboard shell, root page, task components, filter, 404 — parallel)
Batch 5: T015 (dashboard page — integration, needs T012–T014)
Batch 6: T017 (filter integration into dashboard)
Batch 7: T019, T020 (verification)
```

---

## Parallel Example: User Story 3

```bash
# Launch all task components in parallel (different files):
Task: "Create TaskItem component in frontend/components/TaskItem.tsx"
Task: "Create TaskForm component in frontend/components/TaskForm.tsx"
Task: "Create TaskList component in frontend/components/TaskList.tsx"

# Then integrate into dashboard (depends on all three):
Task: "Expand dashboard page with full CRUD in frontend/app/dashboard/page.tsx"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3)

1. Complete Phase 1: Setup (types + API client)
2. Complete Phase 2: Foundational (auth components + pages + layout)
3. Complete Phase 3: US1 (dashboard shell)
4. Complete Phase 4: US2 (root redirect)
5. Complete Phase 5: US3 (full task CRUD)
6. **STOP and VALIDATE**: User can sign up, sign in, create/edit/delete/toggle tasks
7. Demo-ready with core functionality

### Full Implementation

8. Complete Phase 6: US4 (filter + sort)
9. Complete Phase 7: US5 (signout + 404)
10. Complete Phase 8: Polish (type check + build)

### Recommended Sequential Order (Single Agent)

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018 → T019 → T020

---

## Summary

| Metric | Count |
|--------|-------|
| Total tasks | 20 |
| Phase 1 (Setup) | 3 |
| Phase 2 (Foundational) | 6 |
| US1 tasks | 1 |
| US2 tasks | 1 |
| US3 tasks | 4 |
| US4 tasks | 2 |
| US5 tasks | 1 |
| Polish tasks | 2 |
| Parallelizable tasks | 14 (marked [P]) |
| New files created | 14 |
| Modified files | 2 (app/page.tsx, app/layout.tsx) |

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Auth infrastructure (Better Auth, useAuth hook) already exists from foundation layer
- Backend API already implemented — frontend calls it via REST with JWT
- All components are `"use client"` — interactivity required throughout
- No tests included — deferred to 008-testing-strategy
- Commit after each phase for clean git history
