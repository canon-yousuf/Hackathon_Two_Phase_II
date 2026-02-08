# Quickstart: Backend API — All 6 REST Endpoints + Service Layer

**Date**: 2026-02-08

## Prerequisites

- Python 3.13+ installed
- `uv` package manager installed
- Backend dependencies installed (`cd backend && uv sync`)
- `.env` file configured with `DATABASE_URL`, `BETTER_AUTH_SECRET`, `CORS_ORIGINS`
- Neon database accessible with `user` table created by Better Auth

## Starting the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The server starts at `http://localhost:8000`. Swagger UI is at `http://localhost:8000/docs`.

## Verification Steps

### Step 1: Health Check

```bash
curl http://localhost:8000/health
```

Expected: `{"status": "healthy"}`

### Step 2: Create a Task (requires JWT)

```bash
# Replace <TOKEN> with a valid JWT and <USER_ID> with the user's ID from the token
curl -X POST "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk and bread"}'
```

Expected: 201 with created task JSON including `id`, `user_id`, `completed: false`, timestamps.

### Step 3: List Tasks

```bash
curl "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with array of tasks.

### Step 4: List Tasks with Filters

```bash
# Filter by pending
curl "http://localhost:8000/api/<USER_ID>/tasks?status=pending" \
  -H "Authorization: Bearer <TOKEN>"

# Sort by title
curl "http://localhost:8000/api/<USER_ID>/tasks?sort=title" \
  -H "Authorization: Bearer <TOKEN>"
```

### Step 5: Get Single Task

```bash
curl "http://localhost:8000/api/<USER_ID>/tasks/1" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with single task JSON.

### Step 6: Update Task

```bash
curl -X PUT "http://localhost:8000/api/<USER_ID>/tasks/1" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy organic groceries"}'
```

Expected: 200 with updated task. `updated_at` should be later than `created_at`.

### Step 7: Toggle Completion

```bash
curl -X PATCH "http://localhost:8000/api/<USER_ID>/tasks/1/complete" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 200 with task showing `completed: true`.

### Step 8: Delete Task

```bash
curl -X DELETE "http://localhost:8000/api/<USER_ID>/tasks/1" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 204 with no body.

### Step 9: Verify Deletion

```bash
curl "http://localhost:8000/api/<USER_ID>/tasks/1" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 404 `{"detail": "Task not found"}`.

## Error Verification

### Missing Token (401)

```bash
curl "http://localhost:8000/api/<USER_ID>/tasks"
```

Expected: 403 (FastAPI's HTTPBearer returns 403 by default when no credentials; can be 401 depending on configuration).

### Wrong User (403)

```bash
# Use User A's token but User B's user_id in the URL
curl "http://localhost:8000/api/wrong-user-id/tasks" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 403 `{"detail": "Not authorized to access this resource"}`.

### Invalid Input (422)

```bash
# Empty title
curl -X POST "http://localhost:8000/api/<USER_ID>/tasks" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'
```

Expected: 422 with validation error details.

### Invalid Query Parameter (422)

```bash
curl "http://localhost:8000/api/<USER_ID>/tasks?status=unknown" \
  -H "Authorization: Bearer <TOKEN>"
```

Expected: 422 with pattern validation error.

## Swagger UI Testing

Open `http://localhost:8000/docs` in a browser. Click "Authorize" and paste a valid JWT token. Then use the interactive endpoint forms to test all 6 endpoints.
