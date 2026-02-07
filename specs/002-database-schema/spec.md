# Feature Specification: Database Schema

**Feature Branch**: `002-database-schema`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Database Schema for Phase II Todo Full-Stack Web Application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Data Persists Across Sessions (Priority: P1)

A user creates a task with a title and optional description. The
task is stored in the database with the user's identity, a
completion status defaulting to incomplete, and automatic
timestamps. When the user returns later (even after signing out
and back in), all their tasks are present exactly as they left
them.

**Why this priority**: Data persistence is the core purpose of the
database. Without reliable storage and retrieval of task data, the
application has no value.

**Independent Test**: Can be fully tested by creating a task,
verifying it appears in the task list, signing out, signing back
in, and confirming the task is still present with all fields intact.

**Acceptance Scenarios**:

1. **Given** an authenticated user with no tasks,
   **When** they create a task with title "Buy groceries",
   **Then** the task is stored with an auto-generated unique ID,
   the user's identity, completion status of false, and timestamps
   recording the current time.

2. **Given** an authenticated user who created a task yesterday,
   **When** they sign in today and view their tasks,
   **Then** the task is present with the original title, description,
   completion status, and creation timestamp unchanged.

3. **Given** an authenticated user creates a task with a title and
   description,
   **When** the task is stored,
   **Then** the title is preserved exactly (up to 200 characters)
   and the description is preserved exactly (up to 1000 characters).

---

### User Story 2 - User Isolation at the Data Layer (Priority: P1)

Each user's tasks are completely isolated from other users' data.
When a user queries their tasks, only tasks belonging to that
specific user are returned. No database query can accidentally
return tasks from another user.

**Why this priority**: User isolation is a constitutional principle.
The data layer is the last line of defense — if isolation fails
here, it fails everywhere.

**Independent Test**: Can be fully tested by creating tasks for two
different users and verifying that each user's query returns only
their own tasks.

**Acceptance Scenarios**:

1. **Given** User A has 3 tasks and User B has 5 tasks,
   **When** User A queries their tasks,
   **Then** exactly 3 tasks are returned, all belonging to User A.

2. **Given** User A has tasks and User B has tasks,
   **When** User B deletes one of their tasks,
   **Then** User A's tasks are completely unaffected.

3. **Given** a task belongs to User A,
   **When** the system processes a request with User B's identity to
   access that task,
   **Then** the task is not found (the query is scoped to User B).

---

### User Story 3 - Task Lifecycle Operations (Priority: P1)

A user can perform all CRUD operations on their tasks: create a new
task, read one or all tasks, update a task's title or description,
mark a task as complete or incomplete, and delete a task permanently.
Each operation updates the relevant timestamps and maintains data
integrity.

**Why this priority**: Full CRUD support is required for the
hackathon's 5 Basic Level features (Add, Delete, Update, View,
Mark Complete).

**Independent Test**: Can be fully tested by performing each CRUD
operation in sequence and verifying the database state after each
operation.

**Acceptance Scenarios**:

1. **Given** an authenticated user,
   **When** they create a task with title "Read book" and description
   "Chapter 5",
   **Then** the task is stored with completion status false, and both
   creation and update timestamps set to the current time.

2. **Given** a task exists with title "Read book",
   **When** the user updates the title to "Read chapter 6",
   **Then** the title changes, the update timestamp is refreshed,
   and the creation timestamp remains unchanged.

3. **Given** a task exists with completion status false,
   **When** the user marks it as complete,
   **Then** the completion status changes to true and the update
   timestamp is refreshed.

4. **Given** a task exists,
   **When** the user deletes it,
   **Then** the task is permanently removed from the database and
   no longer appears in any query.

---

### User Story 4 - User Account Deletion Cascades to Tasks (Priority: P2)

When a user's account is deleted (by the authentication system),
all tasks belonging to that user are automatically deleted. No
orphaned task records remain in the database.

**Why this priority**: Data integrity is important but this is a
less frequent operation than daily task management. The cascade
ensures no orphaned data accumulates.

**Independent Test**: Can be fully tested by creating tasks for a
user, deleting the user account, and verifying that all associated
tasks are removed.

**Acceptance Scenarios**:

1. **Given** a user has 10 tasks in the database,
   **When** the user's account is deleted,
   **Then** all 10 tasks are automatically removed.

2. **Given** User A and User B both have tasks,
   **When** User A's account is deleted,
   **Then** User B's tasks remain completely intact.

---

### User Story 5 - Efficient Task Queries (Priority: P2)

When a user views their task list, the system can efficiently filter
tasks by completion status and sort by creation date or title. Query
performance remains consistent as the number of tasks grows.

**Why this priority**: Filtering and sorting are required by the API
spec (query parameters on GET list endpoint). Indexes ensure these
operations remain fast as data grows.

**Independent Test**: Can be fully tested by creating multiple tasks
with different completion statuses and creation times, then querying
with filters and verifying correct results are returned in the
expected order.

**Acceptance Scenarios**:

1. **Given** a user has both complete and incomplete tasks,
   **When** they filter by completion status "incomplete",
   **Then** only incomplete tasks are returned.

2. **Given** a user has multiple tasks created at different times,
   **When** they sort by creation date,
   **Then** tasks are returned in the correct chronological order.

3. **Given** a user has 100 tasks,
   **When** they query their task list with filters,
   **Then** results are returned within 1 second.

---

### User Story 6 - Secure Database Connections (Priority: P3)

All connections between the application and the database use
encrypted transport. The database connection string is never
hardcoded and is always loaded from an environment variable. The
connection handles intermittent availability gracefully (serverless
cold starts).

**Why this priority**: Security and reliability are important but
are infrastructure concerns that operate transparently once
configured. They don't affect the user-facing feature set.

**Independent Test**: Can be fully tested by verifying the
connection uses SSL, attempting to connect without the environment
variable (should fail with clear error), and verifying the
connection recovers from a brief interruption.

**Acceptance Scenarios**:

1. **Given** the database connection string includes SSL requirements,
   **When** the application connects to the database,
   **Then** the connection uses encrypted transport.

2. **Given** the database connection string environment variable is
   not set,
   **When** the application attempts to start,
   **Then** it fails with a clear configuration error message.

3. **Given** the database was idle and enters a cold start state,
   **When** the next request arrives,
   **Then** the connection is re-established transparently without
   returning an error to the user.

---

### Edge Cases

- What happens when a task title is empty or exceeds 200 characters?
  The system MUST reject the operation with a validation error.
- What happens when a task description exceeds 1000 characters?
  The system MUST reject the operation with a validation error.
- What happens when a user tries to create a task with a user
  identity that does not exist? The database MUST reject the insert
  due to the referential integrity constraint.
- What happens when two tasks are created at the exact same
  timestamp? Both MUST be stored successfully — timestamps are not
  unique identifiers.
- What happens when the database connection is lost mid-request?
  The system MUST return an appropriate error to the caller rather
  than hanging indefinitely.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store tasks with exactly these attributes:
  unique auto-incrementing identifier, owning user reference, title,
  optional description, completion status, creation timestamp, and
  update timestamp
- **FR-002**: Task title MUST be between 1 and 200 characters and
  is required
- **FR-003**: Task description MUST be at most 1000 characters and
  is optional (nullable)
- **FR-004**: Task completion status MUST default to false (incomplete)
  when a task is created
- **FR-005**: Creation timestamp MUST be automatically set to the
  current time (UTC) when a task is created and MUST NOT change
  thereafter
- **FR-006**: Update timestamp MUST be automatically set to the
  current time (UTC) when a task is created and MUST be refreshed
  whenever the task is modified
- **FR-007**: Each task MUST reference a valid user — the database
  MUST enforce this relationship via a referential integrity
  constraint
- **FR-008**: When a user account is deleted, all tasks belonging to
  that user MUST be automatically deleted (cascade)
- **FR-009**: All task queries MUST be scoped to a specific user —
  no query may return tasks across user boundaries
- **FR-010**: The system MUST support efficient filtering of tasks
  by completion status via an index
- **FR-011**: The system MUST support efficient filtering of tasks
  by owning user via an index
- **FR-012**: The system MUST support efficient sorting of tasks by
  creation date via an index
- **FR-013**: All database connections MUST use encrypted transport
  (SSL/TLS)
- **FR-014**: The database connection string MUST be loaded from an
  environment variable — never hardcoded
- **FR-015**: The connection MUST handle serverless cold starts
  gracefully without returning errors to the user
- **FR-016**: The system MUST provide separate data shapes for
  creating a task (title + optional description), updating a task
  (optional title + optional description + optional completion
  status), and returning a task (all fields)
- **FR-017**: The system MUST NOT expose internal storage models
  directly in API responses — separate response shapes are required
- **FR-018**: All timestamps MUST use UTC timezone
- **FR-019**: The user table is managed entirely by the
  authentication system — the backend MUST NOT write to it

### Key Entities

- **Task**: The primary entity managed by this spec. Represents a
  to-do item belonging to a specific user. Attributes: unique
  auto-incrementing ID (integer), owning user reference (text,
  required), title (1-200 chars, required), description (up to 1000
  chars, optional), completion status (boolean, default false),
  creation timestamp (UTC, auto-set), update timestamp (UTC,
  auto-set and auto-refreshed on modification).
- **User**: Referenced by Task via a referential integrity
  constraint. Managed entirely by the authentication system — this
  spec does not define its schema. The only relevant attribute is
  the unique user ID (text type) used as the reference target.

### Assumptions

- The authentication system creates the user table before any tasks
  are inserted
- The user table has a text-type primary key column representing the
  unique user identifier
- The authentication system also creates session, account, and
  verification tables which this spec does not interact with
- The database supports standard constraints (referential integrity,
  indexes, defaults, not-null)
- Auto-increment for task IDs uses the database's native integer
  sequence mechanism
- The application connects to a single database instance (no read
  replicas or sharding for Phase II)
- Table creation at application startup is sufficient — no
  migration tooling is required for Phase II

## Non-Goals

- No due_date, priority, tags, or categories columns (Phase V)
- No recurring task fields
- No conversation or message tables (Phase III)
- No migration tool required — table creation at startup is
  sufficient for Phase II
- No caching layer
- No full-text search on task content
- No soft delete — tasks are permanently removed on delete
- No audit log or change history for tasks

## Dependencies

- Architecture spec (001-system-architecture) MUST be approved first
- Auth spec will define how the user table is created by the
  authentication system
- API spec will reference the data shapes defined here for
  request/response models
- This spec is consumed by: Database Agent (primary), Backend Agent,
  Auth Agent, Testing Agent

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A task created by a user persists across browser
  sessions — user can sign out, sign back in, and find the task
  unchanged
- **SC-002**: A user with 100 tasks can filter by completion status
  and receive results within 1 second
- **SC-003**: No user can retrieve, modify, or delete another user's
  tasks through any supported operation
- **SC-004**: When a user account is deleted, 100% of that user's
  tasks are removed and no other user's data is affected
- **SC-005**: A task created without a description stores a null
  value, and a task created with a description stores the text
  exactly as provided
- **SC-006**: Creating a task with a title longer than 200 characters
  or an empty title is rejected with a validation error
- **SC-007**: The update timestamp changes every time a task is
  modified, while the creation timestamp remains constant
- **SC-008**: The system recovers from a database cold start within
  5 seconds without returning an error to the end user
- **SC-009**: All database connections use encrypted transport — no
  unencrypted connections are permitted
- **SC-010**: Separate data shapes exist for task creation, task
  update, and task response — the internal storage model is never
  exposed directly
