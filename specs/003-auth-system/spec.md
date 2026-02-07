# Feature Specification: Authentication System

**Feature Branch**: `003-auth-system`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Authentication System for Phase II Todo Full-Stack Web Application"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Signs Up with Email and Password (Priority: P1)

A new user visits the application for the first time. They navigate
to the signup page and enter their name, email address, and password.
The system creates their account, securely hashes their password,
and signs them in automatically. The user is redirected to the
dashboard with full access to task management features.

**Why this priority**: Without signup, no users can exist in the
system. This is the entry point for all functionality.

**Independent Test**: Can be fully tested by visiting the signup
page, entering valid credentials, submitting the form, and
verifying the user lands on the dashboard with an active session.

**Acceptance Scenarios**:

1. **Given** a new user on the signup page,
   **When** they enter a valid name, email, and password and submit,
   **Then** their account is created, they are signed in, and
   redirected to the dashboard.

2. **Given** a user tries to sign up with an email that is already
   registered,
   **When** they submit the signup form,
   **Then** the system displays an error message indicating the
   email is already in use.

3. **Given** a user tries to sign up with an invalid email format,
   **When** they submit the signup form,
   **Then** the system displays a validation error for the email
   field.

4. **Given** a user tries to sign up with a password that is too
   short (fewer than 8 characters),
   **When** they submit the signup form,
   **Then** the system displays a validation error for the password
   field.

---

### User Story 2 - User Signs In with Existing Credentials (Priority: P1)

A returning user visits the application and navigates to the login
page. They enter their email and password. The system verifies
their credentials and issues an authentication token. The user is
redirected to the dashboard with access to their tasks.

**Why this priority**: Signin is required for every returning user
session. Without it, users can only use the app once (at signup).

**Independent Test**: Can be fully tested by signing up a user,
signing out, navigating to the login page, entering correct
credentials, and verifying successful redirect to the dashboard.

**Acceptance Scenarios**:

1. **Given** a registered user on the login page,
   **When** they enter their correct email and password,
   **Then** they are authenticated, issued a token, and redirected
   to the dashboard.

2. **Given** a user on the login page,
   **When** they enter an incorrect password,
   **Then** the system displays an error message (without revealing
   whether the email exists).

3. **Given** a user on the login page,
   **When** they enter an email that is not registered,
   **Then** the system displays the same generic error message as
   an incorrect password (to prevent user enumeration).

---

### User Story 3 - Authenticated Token Secures API Requests (Priority: P1)

After signing in, every request the user makes to the backend API
automatically includes their authentication token. The backend
verifies the token's validity and extracts the user's identity
before processing the request. This happens transparently — the
user never manually handles tokens.

**Why this priority**: Token-based API security is the bridge
between the frontend authentication and the backend data layer.
Without it, the backend cannot verify who is making requests.

**Independent Test**: Can be fully tested by signing in, making an
API call to the task list endpoint, and verifying the request
includes a valid token and the backend accepts it.

**Acceptance Scenarios**:

1. **Given** an authenticated user,
   **When** the frontend makes an API request,
   **Then** the authentication token is automatically attached to
   the request header.

2. **Given** a request with a valid, non-expired token,
   **When** the backend receives the request,
   **Then** the backend verifies the token, extracts the user
   identity, and processes the request.

3. **Given** a request with a valid token where the user identity
   in the token matches the user identity in the URL,
   **When** the backend processes the request,
   **Then** the request succeeds with the expected response.

---

### User Story 4 - Backend Rejects Unauthorized Requests (Priority: P1)

The backend enforces strict authentication on all task endpoints.
Requests without a token, with an expired token, with a tampered
token, or where the token's user identity does not match the URL's
user identity are all rejected with the appropriate error response.

**Why this priority**: Security enforcement is non-negotiable. Every
failure mode must be explicitly handled to prevent unauthorized
data access.

**Independent Test**: Can be fully tested by sending requests to
the backend with various invalid token states and verifying the
correct error codes are returned.

**Acceptance Scenarios**:

1. **Given** a request with no authentication token,
   **When** sent to any task endpoint,
   **Then** the backend returns 401 Unauthorized.

2. **Given** a request with an expired token,
   **When** sent to any task endpoint,
   **Then** the backend returns 401 Unauthorized.

3. **Given** a request with a tampered or invalid token,
   **When** sent to any task endpoint,
   **Then** the backend returns 401 Unauthorized.

4. **Given** a request with a valid token for User A,
   **When** sent to a task endpoint with User B's identity in the
   URL,
   **Then** the backend returns 403 Forbidden.

---

### User Story 5 - User Signs Out and Loses Access (Priority: P2)

An authenticated user clicks the sign out button. The system ends
their session and clears their authentication token. The user is
redirected to the login page. Any subsequent attempt to access
protected pages redirects them to the login page.

**Why this priority**: Signout is important for security (shared
devices) but is used less frequently than signin. The core
functionality works without it.

**Independent Test**: Can be fully tested by signing in, clicking
sign out, and verifying the user cannot access the dashboard or
make API requests.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard,
   **When** they click the sign out button,
   **Then** their session ends, their token is cleared, and they
   are redirected to the login page.

2. **Given** a user who just signed out,
   **When** they try to navigate directly to the dashboard URL,
   **Then** they are redirected to the login page.

3. **Given** a user who just signed out,
   **When** the frontend attempts an API request,
   **Then** no token is attached and the backend returns 401.

---

### User Story 6 - Unauthenticated Users Redirected to Login (Priority: P2)

An unauthenticated user (not signed in) tries to access any
protected page (dashboard or sub-routes). The system automatically
redirects them to the login page. After successful login, they
are taken to the dashboard.

**Why this priority**: Route protection ensures users cannot see
empty or broken pages when not authenticated. It completes the
auth UX but is not strictly required for core functionality.

**Independent Test**: Can be fully tested by clearing all session
data, navigating to the dashboard URL, and verifying a redirect
to the login page occurs.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user,
   **When** they navigate to the dashboard,
   **Then** they are redirected to the login page.

2. **Given** an unauthenticated user,
   **When** they navigate to any route under the dashboard,
   **Then** they are redirected to the login page.

3. **Given** a user on the login page after being redirected,
   **When** they successfully sign in,
   **Then** they are taken to the dashboard.

---

### User Story 7 - Auth System Auto-Manages User Data (Priority: P3)

The authentication system automatically creates and manages the
database tables it needs (user, session, account). The backend
application reads from the user table to verify user existence but
never writes to it. No manual database setup is required for auth
tables.

**Why this priority**: This is infrastructure behavior that happens
automatically. It must work correctly but is invisible to users.

**Independent Test**: Can be fully tested by starting the
application with a fresh database and verifying that signup works
(meaning the auth tables were created automatically).

**Acceptance Scenarios**:

1. **Given** a fresh database with no tables,
   **When** the frontend application starts with the authentication
   system configured,
   **Then** the user, session, and account tables are created
   automatically.

2. **Given** the authentication system manages the user table,
   **When** the backend processes a request,
   **Then** the backend reads from but never writes to the user
   table.

---

### Edge Cases

- What happens when a user submits the signup form with all fields
  empty? The system MUST display validation errors for all required
  fields (name, email, password).
- What happens when a user's token expires while they are actively
  using the app? The next API request MUST return 401, and the
  frontend MUST redirect them to the login page.
- What happens when the shared secret differs between frontend and
  backend? All API requests will fail with 401 because tokens
  cannot be verified.
- What happens when a user opens multiple browser tabs? All tabs
  MUST share the same authentication state — signing out in one
  tab MUST sign out all tabs.
- What happens when the authentication system cannot reach the
  database? Signup and signin MUST fail with a user-friendly error
  message rather than an unhandled exception.
- What happens when a user tries to sign up with a very long email
  or name? The system MUST validate input lengths and reject
  unreasonable values.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to create an account by providing
  a name, email address, and password
- **FR-002**: Users MUST be able to sign in with their email and
  password
- **FR-003**: Users MUST be able to sign out, ending their session
  and clearing their authentication token
- **FR-004**: The system MUST issue an authentication token upon
  successful signup or signin
- **FR-005**: The authentication token MUST contain the user's
  unique identifier, email, and name
- **FR-006**: The authentication token MUST have an expiry time
  (default: 7 days)
- **FR-007**: The frontend MUST automatically attach the
  authentication token to every API request sent to the backend
- **FR-008**: The backend MUST verify the authentication token's
  signature using the shared secret before processing any request
- **FR-009**: The backend MUST extract the user's unique identifier
  from the token and compare it against the user identifier in the
  URL path
- **FR-010**: A request without a token MUST be rejected with 401
  Unauthorized
- **FR-011**: A request with an expired token MUST be rejected with
  401 Unauthorized
- **FR-012**: A request with a tampered or invalid token MUST be
  rejected with 401 Unauthorized
- **FR-013**: A request where the token's user identifier does not
  match the URL's user identifier MUST be rejected with 403
  Forbidden
- **FR-014**: Unauthenticated users MUST be redirected to the login
  page when accessing protected routes
- **FR-015**: After successful login, users MUST be redirected to
  the dashboard
- **FR-016**: Password MUST be at least 8 characters long
- **FR-017**: Email MUST be validated for proper format before
  submission
- **FR-018**: The authentication system MUST securely hash passwords
  — the application MUST NOT implement custom password hashing
- **FR-019**: Authentication tokens MUST NOT be stored in browser
  local storage — the system MUST use secure cookie or in-memory
  storage
- **FR-020**: The shared authentication secret MUST be at least 32
  characters and loaded from an environment variable
- **FR-021**: The authentication system MUST auto-create and manage
  the user, session, and account tables in the database
- **FR-022**: The backend MUST NOT write to the user table — it is
  managed exclusively by the authentication system
- **FR-023**: Login error messages MUST NOT reveal whether a
  specific email address is registered (prevent user enumeration)
- **FR-024**: The backend MUST only accept requests from the
  frontend origin (CORS restriction)

### Key Entities

- **User**: An authenticated person using the application. Managed
  by the authentication system. Attributes: unique identifier,
  name, email, hashed password, creation timestamp. The backend
  reads this data but never writes to it.
- **Session**: An active authentication session for a user. Managed
  by the authentication system. Created on signin, destroyed on
  signout. Associated with token issuance.
- **Account**: A link between a user and their authentication
  method (email/password). Managed by the authentication system.
- **Authentication Token**: A cryptographically signed token issued
  to a user after successful authentication. Contains: user
  identifier (sub claim), email, name, and expiry. Used by the
  frontend to authenticate API requests to the backend.

### Assumptions

- Email/password is the only authentication method for Phase II
  (no OAuth, SSO, or social login)
- The authentication system handles all password hashing internally
  using secure algorithms
- Token signing uses the HMAC-SHA256 algorithm with the shared
  secret
- The shared secret is generated once and configured identically
  on both frontend and backend via environment variables
- The authentication system's auto-created tables do not conflict
  with the application's task table
- Session duration matches the token expiry (7 days)
- No refresh token mechanism is needed for Phase II — users
  re-authenticate when the token expires
- A placeholder `.env.example` file is provided with sample values
  for all required environment variables

## Non-Goals

- No OAuth or social login providers (Google, GitHub, etc.)
- No email verification flow
- No password reset or forgot password flow
- No role-based access control (admin vs user)
- No refresh token rotation
- No two-factor authentication
- No rate limiting on login attempts
- No account lockout after failed attempts
- No password complexity rules beyond minimum length
- No "remember me" functionality

## Dependencies

- Architecture spec (001-system-architecture) — defines service
  boundaries and data flow for auth
- Database spec (002-database-schema) — defines that the user table
  is managed by the authentication system
- API spec will reference this spec for endpoint security
  requirements
- Frontend Pages spec will reference this spec for login/signup
  page requirements

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can create an account and reach the
  dashboard within 30 seconds of starting the signup process
- **SC-002**: A returning user can sign in and reach the dashboard
  within 15 seconds
- **SC-003**: After signing out, a user cannot access any protected
  page or make any authenticated API request
- **SC-004**: 100% of API requests without a valid token are rejected
  with the appropriate error code (401 or 403)
- **SC-005**: A user's token expires after 7 days, requiring them
  to sign in again
- **SC-006**: No API request can succeed when the token's user
  identity does not match the URL's user identity
- **SC-007**: Login error messages never reveal whether a specific
  email address is registered in the system
- **SC-008**: All authentication secrets are loaded from environment
  variables — no secrets appear in source code
- **SC-009**: The authentication system creates all required tables
  automatically on first run — no manual database setup for auth
- **SC-010**: Password validation rejects passwords shorter than 8
  characters at the signup form
