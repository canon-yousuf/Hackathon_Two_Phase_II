# Feature Specification: System Architecture

**Feature Branch**: `001-system-architecture`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "System Architecture for Phase II Todo Full-Stack Web Application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Frontend Communicates with Backend via REST (Priority: P1)

A user opens the web application in their browser. The frontend
application loads and, upon user interaction (e.g., viewing tasks,
creating a task), sends HTTP requests to the backend API. Every
request includes a JWT Bearer token in the Authorization header.
The backend receives the request, verifies the JWT, processes the
business logic, queries the database, and returns a JSON response.
The frontend renders the response to the user.

**Why this priority**: This is the foundational data flow. Without
frontend-to-backend communication, no feature works. Every other
user story depends on this communication channel being established.

**Independent Test**: Can be fully tested by starting both services
independently, obtaining a valid JWT token, and making an
authenticated API call from the frontend that returns task data
from the database.

**Acceptance Scenarios**:

1. **Given** the frontend and backend are both running independently,
   **When** the frontend sends a GET request to `/api/{user_id}/tasks`
   with a valid JWT Bearer token,
   **Then** the backend returns a 200 response with JSON task data
   belonging to that user.

2. **Given** the frontend and backend are both running independently,
   **When** the frontend sends a POST request to
   `/api/{user_id}/tasks` with a valid JWT Bearer token and task data,
   **Then** the backend creates the task in the database and returns
   a 201 response with the created task.

3. **Given** the backend is running,
   **When** any client sends a GET request to `/health`,
   **Then** the backend returns a 200 response confirming the service
   is operational.

---

### User Story 2 - Backend Verifies JWT and Enforces User Access (Priority: P1)

A user attempts to access task data through the API. The backend
extracts the JWT from the Authorization header, verifies its
signature using the shared secret, extracts the user ID from the
token claims, and compares it against the user ID in the URL path.
If the token is missing, invalid, or the user IDs do not match, the
request is rejected with the appropriate error response.

**Why this priority**: Security and user isolation are non-negotiable.
Without JWT verification and user ID enforcement, any user could
access any other user's data, violating the core User Isolation
principle.

**Independent Test**: Can be fully tested by sending requests to the
backend with various token states (valid, expired, missing, wrong
user) and verifying the correct HTTP status codes are returned.

**Acceptance Scenarios**:

1. **Given** a valid JWT token for user A,
   **When** a request is made to `/api/{user_A_id}/tasks`,
   **Then** the backend processes the request and returns 200.

2. **Given** a valid JWT token for user A,
   **When** a request is made to `/api/{user_B_id}/tasks`,
   **Then** the backend rejects the request with 403 Forbidden.

3. **Given** no Authorization header is present,
   **When** a request is made to any `/api/{user_id}/tasks` endpoint,
   **Then** the backend rejects the request with 401 Unauthorized.

4. **Given** an expired or malformed JWT token,
   **When** a request is made to any `/api/{user_id}/tasks` endpoint,
   **Then** the backend rejects the request with 401 Unauthorized.

---

### User Story 3 - User Signs Up and Signs In via Better Auth (Priority: P1)

A new user visits the application, fills in their email and password,
and creates an account. Better Auth (running within the frontend
application) handles account creation, password hashing, and session
management. The user's account data is persisted in the shared
database. After signup (or subsequent signin), the user receives a
JWT token that the frontend stores and attaches to all API requests.

**Why this priority**: Without authentication, users cannot obtain
JWT tokens, and without JWT tokens, no API requests can succeed.
Authentication is the gateway to all functionality.

**Independent Test**: Can be fully tested by visiting the signup page,
creating an account, signing in, and verifying that a JWT token is
issued and stored for subsequent API calls.

**Acceptance Scenarios**:

1. **Given** a new user with a valid email and password,
   **When** they submit the signup form,
   **Then** Better Auth creates their account in the database and
   issues a JWT token.

2. **Given** an existing user with correct credentials,
   **When** they submit the signin form,
   **Then** Better Auth authenticates them and issues a JWT token.

3. **Given** an authenticated user with a valid JWT token,
   **When** the frontend makes an API request to the backend,
   **Then** the JWT token is automatically included in the
   Authorization header.

---

### User Story 4 - Task Data Persists in Shared Database (Priority: P2)

A user creates, updates, or deletes tasks through the application.
All task data is stored in a shared database that both Better Auth
(for user accounts) and the backend (for task operations) connect to.
Task data persists across sessions — when a user signs out and signs
back in, their tasks are still available.

**Why this priority**: Data persistence is essential for a functional
application but depends on the communication (US1) and auth (US2,
US3) stories being in place first.

**Independent Test**: Can be fully tested by creating tasks, signing
out, signing back in, and verifying all tasks are still present and
unchanged.

**Acceptance Scenarios**:

1. **Given** an authenticated user creates a task,
   **When** they sign out and sign back in,
   **Then** the task is still present in their task list.

2. **Given** the backend is connected to the database with SSL,
   **When** a task CRUD operation is performed,
   **Then** the data is persisted and the connection uses encrypted
   transport.

3. **Given** Better Auth manages user accounts in the same database,
   **When** the backend reads user data for JWT verification,
   **Then** the backend never writes to the user table — it is
   read-only for the backend.

---

### User Story 5 - Services Deploy and Run Independently (Priority: P2)

The frontend and backend are independently deployable services. The
frontend can be deployed to a hosting platform without the backend
being co-located. The backend can be started via a standard command
without the frontend running. Both services are configured entirely
through environment variables — no hardcoded URLs, secrets, or
connection strings.

**Why this priority**: Independent deployability validates that
service boundaries are correctly drawn and that the system does not
have hidden coupling.

**Independent Test**: Can be fully tested by starting each service
in isolation, verifying it starts without errors, and confirming
configuration is loaded from environment variables.

**Acceptance Scenarios**:

1. **Given** the backend environment variables are set,
   **When** the backend is started via `uvicorn`,
   **Then** it starts successfully and responds to health checks at
   `/health`.

2. **Given** the frontend environment variables are set,
   **When** the frontend is started via `npm run dev`,
   **Then** it starts successfully and renders the application.

3. **Given** no `.env` file exists but all environment variables are
   set in the shell,
   **Then** both services start and operate correctly.

---

### User Story 6 - CORS Restricts Backend Access to Frontend Only (Priority: P3)

The backend is configured to accept requests only from the frontend
origin. Any request from an unauthorized origin is rejected by the
CORS middleware before reaching route handlers.

**Why this priority**: CORS is a security hardening measure. The
system is functional without it, but it prevents unauthorized
cross-origin access in production.

**Independent Test**: Can be fully tested by making requests from
the allowed frontend origin (succeeds) and from an unauthorized
origin (fails with CORS error).

**Acceptance Scenarios**:

1. **Given** the backend CORS is configured with the frontend origin,
   **When** the frontend makes a request to the backend,
   **Then** the request is allowed and processed.

2. **Given** the backend CORS is configured with the frontend origin,
   **When** an unknown origin makes a request to the backend,
   **Then** the request is rejected by CORS middleware.

---

### Edge Cases

- What happens when the database connection is unavailable at startup?
  The backend MUST fail fast with a clear error message rather than
  starting in a degraded state.
- What happens when the JWT secret differs between frontend and
  backend? All API requests will fail with 401 because the backend
  cannot verify tokens signed with a different secret.
- What happens when CORS_ORIGINS is not set? The backend MUST reject
  all cross-origin requests (fail-closed behavior).
- What happens when DATABASE_URL is missing? Both services MUST
  refuse to start with a clear configuration error.
- What happens when the frontend cannot reach the backend? The
  frontend MUST display a user-friendly error message indicating
  the service is unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST consist of exactly two services: a frontend
  web application and a backend API server
- **FR-002**: Frontend and backend MUST communicate exclusively via
  REST API over HTTP/HTTPS
- **FR-003**: All API requests from frontend to backend MUST include
  a JWT Bearer token in the Authorization header
- **FR-004**: Backend MUST verify the JWT signature using the shared
  secret before processing any request
- **FR-005**: Backend MUST compare the user ID from the JWT token
  against the user ID in the URL path and reject mismatches with 403
- **FR-006**: Backend MUST expose a health check endpoint at
  GET `/health` that returns 200 when the service is operational
- **FR-007**: Backend MUST expose exactly 6 REST endpoints under
  `/api/{user_id}/tasks` for task CRUD operations
- **FR-008**: All task data MUST be persisted in a shared database
  accessible by both services
- **FR-009**: Database connections MUST use SSL/TLS encryption
- **FR-010**: Frontend MUST handle user authentication (signup,
  signin, signout) via Better Auth
- **FR-011**: Better Auth MUST manage the user table — the backend
  MUST NOT write to it
- **FR-012**: Backend MUST configure CORS to accept requests only
  from the frontend origin
- **FR-013**: Both services MUST be configurable entirely through
  environment variables
- **FR-014**: Frontend MUST route all API calls through a single
  API client module — no direct fetch calls in components
- **FR-015**: Backend MUST follow thin route handler pattern — no
  business logic or database calls in route handlers
- **FR-016**: Both services MUST be independently startable and
  deployable

### Key Entities

- **User**: Represents an authenticated person using the application.
  Managed exclusively by Better Auth. Key attributes: unique ID,
  email, hashed password, creation timestamp. The backend reads user
  data but never writes to it.
- **Task**: Represents a to-do item belonging to a specific user.
  Key attributes: unique ID, title, completion status, owning user
  reference, creation timestamp, update timestamp. All task
  operations are scoped to the owning user.
- **Session**: Represents an active authentication session. Managed
  exclusively by Better Auth. Used to issue and track JWT tokens.
- **Account**: Represents an authentication provider link for a user.
  Managed exclusively by Better Auth.

### Assumptions

- Better Auth uses email/password authentication (no OAuth/SSO for
  Phase II)
- JWT tokens contain a `sub` claim with the user's unique ID
- The database schema for user, session, and account tables is
  determined by Better Auth's conventions
- Standard web application performance expectations apply (pages
  load in under 3 seconds, API responses in under 1 second)
- The application serves a single-digit number of concurrent users
  during hackathon evaluation (no high-scale requirements)

## Service Boundaries *(mandatory)*

### Frontend Service

- **Responsibilities**: UI rendering, user authentication (Better
  Auth), JWT token management, API calls to backend, form handling,
  client-side routing
- **Does NOT**: Access the database directly, perform business logic
  on task data, verify JWT tokens, manage CORS
- **Communicates with**: Backend API (via HTTP REST), Neon database
  (via Better Auth only, for auth tables)

### Backend Service

- **Responsibilities**: JWT verification, route handling, business
  logic, database queries for tasks, CORS enforcement, input
  validation, error responses
- **Does NOT**: Render UI, issue JWT tokens, manage user signup/
  signin, hash passwords, write to user/session/account tables
- **Communicates with**: Neon database (for task table reads/writes
  and user table reads)

### Database

- **Tables managed by Better Auth**: user, session, account,
  verification (frontend writes, backend reads)
- **Tables managed by Backend**: tasks (backend reads/writes)
- **Shared**: Both services connect to the same database instance
- **Security**: All connections MUST use SSL (`sslmode=require`)

## Data Flow *(mandatory)*

### User Signup/Signin Flow

1. User enters credentials in the browser
2. Frontend sends credentials to Better Auth (running in Next.js)
3. Better Auth validates credentials and creates/verifies user
   record in the database
4. Better Auth issues a JWT token signed with BETTER_AUTH_SECRET
5. Frontend stores the JWT token for subsequent API calls

### Task Operation Flow

1. User interacts with the task UI in the browser
2. Frontend API client attaches JWT token to Authorization header
3. Frontend sends HTTP request to backend API endpoint
4. Backend middleware extracts and verifies JWT token
5. Backend middleware extracts user ID from JWT and compares to URL
6. Route handler delegates to service layer
7. Service layer performs database query (scoped to user ID)
8. Backend returns JSON response
9. Frontend renders the response

### Environment Variable Flow

- `BETTER_AUTH_SECRET`: Frontend uses it to sign JWTs; Backend uses
  it to verify JWTs. MUST be identical on both sides.
- `DATABASE_URL`: Both services use this to connect to Neon. MUST
  include `sslmode=require`.
- `NEXT_PUBLIC_API_URL`: Frontend uses this as the base URL for all
  backend API calls.
- `CORS_ORIGINS`: Backend uses this to configure allowed origins.

## Non-Goals

- No CI/CD pipeline (Phase V)
- No containerization with Docker/Kubernetes (Phase IV)
- No event-driven architecture or message queues (Phase V)
- No AI chatbot or MCP integration (Phase III)
- No intermediate/advanced task features — recurring tasks, due
  dates, priorities (Phase V)
- No mobile responsiveness requirements beyond basic Tailwind
- No specific UI design system or component library mandated
- No WebSocket or GraphQL — REST only for Phase II
- No microservices — exactly 2 services

## Dependencies

- Constitution v1.0.0 MUST be committed before this spec (done)
- This spec MUST be approved before any other spec is written
- All subsequent specs (database, auth, API, task-crud,
  frontend-pages, frontend-components, testing) inherit from this
  architecture and MUST NOT contradict it

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Both services start independently without errors when
  all required environment variables are provided
- **SC-002**: A user can sign up, sign in, and receive a JWT token
  within 10 seconds of form submission
- **SC-003**: An authenticated user can create, read, update, and
  delete tasks with all changes persisting across browser sessions
- **SC-004**: A request with a missing or invalid JWT token is
  rejected within 1 second with the appropriate error code (401)
- **SC-005**: A request where the JWT user ID does not match the URL
  user ID is rejected within 1 second with a 403 error
- **SC-006**: The system supports exactly 6 task endpoints, and each
  returns the correct HTTP status code for success and error cases
- **SC-007**: No user can view, modify, or delete another user's
  task data under any circumstance
- **SC-008**: The backend health check endpoint returns 200 within
  2 seconds
- **SC-009**: All database connections use SSL encryption
- **SC-010**: A request from an unauthorized origin is blocked by
  CORS before reaching any route handler
