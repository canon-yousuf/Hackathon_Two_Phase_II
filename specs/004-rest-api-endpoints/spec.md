# Feature Specification: REST API Endpoints

**Feature Branch**: `004-rest-api-endpoints`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "REST API Endpoints for Phase II Todo Full-Stack Web Application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Views Their Task List (Priority: P1)

An authenticated user opens the application and sees their list of
tasks. They can filter by completion status (all, pending, completed)
and sort by creation date or title. The system returns only tasks
belonging to that user, never another user's data.

**Why this priority**: Viewing tasks is the most fundamental
operation. Every user session starts with seeing their task list.
Without this, no other task operation is meaningful.

**Independent Test**: Can be fully tested by creating several tasks
with different completion statuses, then requesting the list with
various filter and sort combinations and verifying the correct
tasks are returned in the correct order.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 5 tasks,
   **When** they request their task list with no filters,
   **Then** all 5 tasks are returned with status 200, sorted by
   creation date (default).

2. **Given** an authenticated user with 3 pending and 2 completed
   tasks,
   **When** they request their task list with status filter "pending",
   **Then** only the 3 pending tasks are returned with status 200.

3. **Given** an authenticated user with 3 pending and 2 completed
   tasks,
   **When** they request their task list with status filter
   "completed",
   **Then** only the 2 completed tasks are returned with status 200.

4. **Given** an authenticated user with multiple tasks,
   **When** they request their task list sorted by title,
   **Then** tasks are returned in alphabetical order by title.

5. **Given** an authenticated user with no tasks,
   **When** they request their task list,
   **Then** an empty array is returned with status 200.

---

### User Story 2 - User Creates a New Task (Priority: P1)

An authenticated user creates a new task by providing a title and
an optional description. The system validates the input, creates
the task associated with the user, and returns the complete task
data including the auto-generated ID and timestamps.

**Why this priority**: Creating tasks is the second most essential
operation. Without it, the task list would always be empty.

**Independent Test**: Can be fully tested by sending a create
request with a valid title, verifying the response includes all
fields with correct defaults, and confirming the task appears in
subsequent list requests.

**Acceptance Scenarios**:

1. **Given** an authenticated user,
   **When** they submit a new task with title "Buy groceries",
   **Then** the task is created and returned with status 201,
   including an auto-generated ID, completion status false, and
   both timestamps set to the current time.

2. **Given** an authenticated user,
   **When** they submit a new task with title "Read book" and
   description "Chapter 5 of Clean Code",
   **Then** the task is created with both title and description
   and returned with status 201.

3. **Given** an authenticated user,
   **When** they submit a new task with no title (empty or missing),
   **Then** the request is rejected with status 422 and an error
   message indicating the title is required.

4. **Given** an authenticated user,
   **When** they submit a new task with a title exceeding 200
   characters,
   **Then** the request is rejected with status 422 and an error
   message indicating the title is too long.

5. **Given** an authenticated user,
   **When** they submit a new task with a description exceeding
   1000 characters,
   **Then** the request is rejected with status 422.

---

### User Story 3 - User Views a Single Task (Priority: P1)

An authenticated user requests the details of a specific task by
its ID. The system returns the complete task data if it exists and
belongs to the user.

**Why this priority**: Viewing a single task is required for the
task detail view and for edit/delete confirmation flows.

**Independent Test**: Can be fully tested by creating a task,
requesting it by ID, and verifying all fields match what was
created.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns a task with ID 42,
   **When** they request task 42,
   **Then** the complete task data is returned with status 200.

2. **Given** an authenticated user,
   **When** they request a task ID that does not exist,
   **Then** the request returns status 404 with an error message.

3. **Given** User A owns task 42 and User B is authenticated,
   **When** User B requests task 42 using User A's endpoint path,
   **Then** the request returns status 403 (user ID mismatch).

---

### User Story 4 - User Updates a Task (Priority: P1)

An authenticated user updates an existing task's title and/or
description. The system validates the input, applies the changes,
refreshes the update timestamp, and returns the updated task.

**Why this priority**: Updating tasks is one of the 5 Basic Level
hackathon features. Users need to correct typos and refine task
descriptions.

**Independent Test**: Can be fully tested by creating a task,
updating its title, and verifying the returned data reflects the
change with an updated timestamp while the creation timestamp
remains unchanged.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns a task,
   **When** they update the task's title to "Updated title",
   **Then** the task is updated and returned with status 200,
   the update timestamp is refreshed, and the creation timestamp
   is unchanged.

2. **Given** an authenticated user who owns a task,
   **When** they update only the description,
   **Then** the title remains unchanged and only the description
   and update timestamp are modified.

3. **Given** an authenticated user,
   **When** they send an update request with all fields null
   (nothing to update),
   **Then** the request is rejected with status 422.

4. **Given** an authenticated user,
   **When** they try to update a task that does not exist,
   **Then** the request returns status 404.

---

### User Story 5 - User Deletes a Task (Priority: P1)

An authenticated user permanently deletes a task they own. The
system removes the task from the database and confirms the deletion.
The task no longer appears in any subsequent queries.

**Why this priority**: Deleting tasks is one of the 5 Basic Level
hackathon features. Users need to remove tasks they no longer need.

**Independent Test**: Can be fully tested by creating a task,
deleting it, verifying a 204 response with no body, and confirming
the task no longer appears in the list.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns a task,
   **When** they delete the task,
   **Then** the task is removed and the response is status 204
   with no body.

2. **Given** an authenticated user,
   **When** they try to delete a task that does not exist,
   **Then** the request returns status 404.

3. **Given** an authenticated user who deleted a task,
   **When** they subsequently request their task list,
   **Then** the deleted task does not appear.

---

### User Story 6 - User Toggles Task Completion (Priority: P1)

An authenticated user marks a task as complete or toggles it back
to incomplete. The system flips the completion status, refreshes the
update timestamp, and returns the updated task.

**Why this priority**: Marking tasks complete is one of the 5 Basic
Level hackathon features and is the primary way users track progress.

**Independent Test**: Can be fully tested by creating a task
(default incomplete), toggling it to complete, verifying the status
changed, then toggling again to verify it returns to incomplete.

**Acceptance Scenarios**:

1. **Given** an authenticated user who owns an incomplete task,
   **When** they toggle the task's completion,
   **Then** the task's completion status changes to true, the update
   timestamp is refreshed, and the task is returned with status 200.

2. **Given** an authenticated user who owns a completed task,
   **When** they toggle the task's completion,
   **Then** the task's completion status changes to false, the update
   timestamp is refreshed, and the task is returned with status 200.

3. **Given** an authenticated user,
   **When** they try to toggle a task that does not exist,
   **Then** the request returns status 404.

---

### User Story 7 - API Rejects Unauthorized Access (Priority: P1)

Every endpoint enforces authentication and user isolation. Requests
without valid credentials are rejected. Requests targeting another
user's data are rejected. The API never leaks data across user
boundaries.

**Why this priority**: Security is non-negotiable per the
constitution. Every endpoint MUST enforce this before processing
any business logic.

**Independent Test**: Can be fully tested by sending requests
without a token (401), with an expired token (401), and with a
valid token targeting another user's path (403).

**Acceptance Scenarios**:

1. **Given** a request with no authentication token,
   **When** sent to any endpoint,
   **Then** the response is status 401 with an error message.

2. **Given** a request with an expired or invalid token,
   **When** sent to any endpoint,
   **Then** the response is status 401 with an error message.

3. **Given** a request with a valid token for User A,
   **When** sent to any endpoint under User B's path,
   **Then** the response is status 403 with an error message.

---

### User Story 8 - API Validates All Input (Priority: P2)

Every endpoint validates its input and returns clear error messages
when validation fails. Invalid query parameters, missing required
fields, and out-of-range values all produce 422 responses with
descriptive error details.

**Why this priority**: Input validation prevents bad data from
entering the system and provides clear feedback to the frontend
for user-facing error messages.

**Independent Test**: Can be fully tested by sending requests with
various invalid inputs and verifying each returns 422 with a
descriptive error.

**Acceptance Scenarios**:

1. **Given** a list request with an invalid status filter value
   (e.g., "unknown"),
   **When** the request is processed,
   **Then** the response is status 422 with an error describing the
   valid values.

2. **Given** a list request with an invalid sort value,
   **When** the request is processed,
   **Then** the response is status 422 with an error describing the
   valid values.

3. **Given** a create request with a description exceeding 1000
   characters,
   **When** the request is processed,
   **Then** the response is status 422 with a descriptive error.

---

### Edge Cases

- What happens when a user creates a task with a title of exactly
  1 character? The system MUST accept it as valid.
- What happens when a user creates a task with a title of exactly
  200 characters? The system MUST accept it as valid.
- What happens when a user creates a task with a description of
  exactly 1000 characters? The system MUST accept it as valid.
- What happens when a user sends a PUT request with only a title
  and no description field? Only the title MUST be updated; the
  description MUST remain unchanged.
- What happens when a user sends a PUT request with description set
  to null? The description MUST be cleared (set to null).
- What happens when a user sends a task ID that is not a valid
  integer? The system MUST return 422 (not 500).
- What happens when two users create tasks simultaneously? Both
  tasks MUST be created successfully with unique IDs.
- What happens when the list endpoint is called with both status
  and sort parameters? Both MUST be applied together.

## Requirements *(mandatory)*

### Functional Requirements

#### Endpoint: List Tasks

- **FR-001**: GET request to the task list endpoint MUST return an
  array of the authenticated user's tasks with status 200
- **FR-002**: The endpoint MUST support a status query parameter
  accepting values: "all" (default), "pending", "completed"
- **FR-003**: The endpoint MUST support a sort query parameter
  accepting values: "created" (default), "title"
- **FR-004**: When status is "pending", only tasks with completion
  status false MUST be returned
- **FR-005**: When status is "completed", only tasks with completion
  status true MUST be returned
- **FR-006**: When sort is "created", tasks MUST be ordered by
  creation timestamp (newest first)
- **FR-007**: When sort is "title", tasks MUST be ordered
  alphabetically by title
- **FR-008**: Invalid query parameter values MUST return status 422

#### Endpoint: Create Task

- **FR-009**: POST request with a valid title MUST create a task
  and return it with status 201
- **FR-010**: The request body MUST accept title (string, 1-200
  characters, required) and description (string, up to 1000
  characters, optional)
- **FR-011**: Title MUST NOT be empty, null, or missing — violation
  returns status 422
- **FR-012**: Title exceeding 200 characters MUST return status 422
- **FR-013**: Description exceeding 1000 characters MUST return
  status 422
- **FR-014**: The created task MUST default to completion status
  false, with both timestamps set to the current time

#### Endpoint: Get Single Task

- **FR-015**: GET request with a valid task ID MUST return the
  complete task with status 200
- **FR-016**: GET request with a non-existent task ID MUST return
  status 404

#### Endpoint: Update Task

- **FR-017**: PUT request with at least one non-null field (title
  or description) MUST update the task and return it with status 200
- **FR-018**: Only provided fields MUST be updated — omitted fields
  MUST remain unchanged
- **FR-019**: A field explicitly set to null MUST clear that field
  (applicable to description)
- **FR-020**: PUT request with all fields null or empty MUST return
  status 422
- **FR-021**: PUT request for a non-existent task MUST return
  status 404
- **FR-022**: The update timestamp MUST be refreshed on every
  successful update

#### Endpoint: Delete Task

- **FR-023**: DELETE request for an existing task MUST remove it
  and return status 204 with no response body
- **FR-024**: DELETE request for a non-existent task MUST return
  status 404
- **FR-025**: A deleted task MUST NOT appear in any subsequent
  queries

#### Endpoint: Toggle Completion

- **FR-026**: PATCH request to the toggle endpoint MUST flip the
  task's completion status (false → true or true → false)
- **FR-027**: The toggled task MUST be returned with status 200
- **FR-028**: PATCH request for a non-existent task MUST return
  status 404
- **FR-029**: The update timestamp MUST be refreshed on every
  successful toggle

#### Cross-Cutting Requirements

- **FR-030**: All endpoints MUST require a valid authentication
  token — missing, invalid, or expired tokens MUST return status 401
- **FR-031**: All endpoints MUST verify the user identity in the
  token matches the user identity in the URL path — mismatch MUST
  return status 403
- **FR-032**: All responses MUST use JSON content type
- **FR-033**: Task responses MUST include: id, user_id, title,
  description, completed, created_at, updated_at
- **FR-034**: Error responses MUST include: detail (string
  describing the error) and status_code (integer)
- **FR-035**: Route handlers MUST be thin — all business logic
  MUST be delegated to a service layer

### Key Entities

- **Task** (response shape): The data returned for each task in API
  responses. Fields: unique integer ID, owning user identifier
  (text), title (string, 1-200 chars), description (string or null,
  up to 1000 chars), completed (boolean), created_at (timestamp,
  UTC), updated_at (timestamp, UTC).
- **Task Create** (request shape): The data accepted when creating
  a task. Fields: title (string, 1-200 chars, required), description
  (string, up to 1000 chars, optional).
- **Task Update** (request shape): The data accepted when updating
  a task. Fields: title (string, 1-200 chars, optional), description
  (string or null, up to 1000 chars, optional). At least one field
  MUST be provided.
- **Error** (response shape): The data returned for error responses.
  Fields: detail (string), status_code (integer).

### Assumptions

- The task list endpoint returns all matching tasks without
  pagination (no limit/offset for Phase II)
- Sort by "created" means descending order (newest first) as this
  is the most useful default for a todo app
- Sort by "title" means ascending alphabetical order
- The toggle endpoint has no request body — it simply flips the
  current completion status
- Task IDs are integers, auto-incremented by the database
- The health check endpoint (GET /health) is defined in the
  architecture spec and not counted among these 6 task endpoints
- The backend validates the authentication token before any route
  handler logic executes

## Non-Goals

- No pagination (limit/offset parameters — Phase V)
- No keyword search query parameter (Phase V)
- No bulk operations (delete multiple, update multiple tasks)
- No file upload or attachment endpoints
- No WebSocket or streaming endpoints
- No authentication endpoints — the authentication system handles
  its own routes on the frontend
- No sort direction parameter (ascending/descending toggle)
- No filtering by date range

## Dependencies

- Architecture spec (001-system-architecture) — defines service
  boundaries and REST communication pattern
- Database spec (002-database-schema) — defines the Task entity
  fields and constraints
- Auth spec (003-auth-system) — defines JWT verification and user
  identity enforcement for all endpoints
- Frontend spec will reference these endpoints for the API client

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The system exposes exactly 6 task endpoints, each
  returning the correct status code for success and every defined
  error case
- **SC-002**: A user can create a task and see it in their task
  list within 2 seconds
- **SC-003**: A user can filter their task list by completion status
  and receive only matching tasks
- **SC-004**: A user can sort their task list by creation date or
  title and receive tasks in the correct order
- **SC-005**: Creating a task with invalid input (empty title, title
  too long, description too long) returns an error with a clear
  message within 1 second
- **SC-006**: Deleting a task results in the task permanently
  disappearing from all subsequent queries
- **SC-007**: Toggling a task's completion status changes it from
  complete to incomplete or vice versa, verifiable by fetching the
  task immediately after
- **SC-008**: 100% of requests without valid authentication are
  rejected before any task data is accessed
- **SC-009**: 100% of requests targeting another user's path are
  rejected with a 403 error
- **SC-010**: Every error response includes a human-readable detail
  message and the corresponding status code
