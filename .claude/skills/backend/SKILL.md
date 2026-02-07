---
name: backend
description: FastAPI backend patterns — routes, service layer, error handling, CORS, Pydantic schemas, and Neon PostgreSQL integration for the Todo API.
---

# Backend Skill — FastAPI Routes, Request/Response Handling, DB Connection

## Overview
This skill provides the complete backend implementation pattern for a **Python FastAPI** server with **SQLModel ORM**, **JWT authentication**, and **RESTful API endpoints** connecting to **Neon Serverless PostgreSQL**.

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, CORS, lifespan
│   ├── config.py               # Settings from env vars
│   ├── db.py                   # Neon engine + session dependency
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py             # SQLModel table + schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py            # Task CRUD endpoints
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py             # JWT verification
│   └── services/
│       ├── __init__.py
│       └── task_service.py     # Business logic (DB queries)
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_tasks.py
│   └── test_auth.py
├── CLAUDE.md
├── pyproject.toml
└── .env.example
```

---

## App Entry Point

**File**: `backend/app/main.py`
```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.db import create_db_and_tables
from app.routes.tasks import router as tasks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables. Shutdown: cleanup."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Todo API",
    description="Phase II Todo Full-Stack Web Application",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(tasks_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

## Config

**File**: `backend/app/config.py`
```python
import os
from dataclasses import dataclass


@dataclass
class Settings:
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "")
    BETTER_AUTH_SECRET: str = os.environ.get("BETTER_AUTH_SECRET", "")
    CORS_ORIGINS: str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")


settings = Settings()
```

---

## Route Handlers

**File**: `backend/app/routes/tasks.py`

### Pattern Rules
- Routes are **thin** — they validate input, call services, return responses
- **No business logic** in routes — all logic lives in `services/`
- Every route depends on `get_current_user` for JWT auth
- Every route calls `enforce_user_access()` to match URL user_id with token
- Return proper HTTP status codes

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.db import get_session
from app.middleware.auth import get_current_user, enforce_user_access
from app.models.task import TaskCreate, TaskUpdate, TaskResponse
from app.services import task_service

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    user_id: str,
    status_filter: str = Query("all", alias="status", pattern="^(all|pending|completed)$"),
    sort: str = Query("created", pattern="^(created|title)$"),
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """List all tasks for the authenticated user."""
    enforce_user_access(user_id, current_user)
    return task_service.get_tasks(session, user_id, status=status_filter, sort=sort)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    data: TaskCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Create a new task."""
    enforce_user_access(user_id, current_user)
    return task_service.create_task(session, user_id, data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Get a single task by ID."""
    enforce_user_access(user_id, current_user)
    task = task_service.get_task(session, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    task_id: int,
    data: TaskUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Update a task's title or description."""
    enforce_user_access(user_id, current_user)
    task = task_service.update_task(session, user_id, task_id, data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Delete a task."""
    enforce_user_access(user_id, current_user)
    deleted = task_service.delete_task(session, user_id, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_complete(
    user_id: str,
    task_id: int,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Toggle task completion status."""
    enforce_user_access(user_id, current_user)
    task = task_service.toggle_complete(session, user_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

---

## Error Handling

### Standardized Error Response
**File**: `backend/app/schemas/error.py`
```python
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None
    status_code: int
```

### Global Exception Handler
Add to `main.py`:
```python
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "status_code": 500,
        },
    )
```

### HTTP Status Code Reference

| Status | When to Use |
|--------|-------------|
| 200 | Successful GET, PUT, PATCH |
| 201 | Successful POST (resource created) |
| 204 | Successful DELETE (no content returned) |
| 400 | Bad request (malformed input) |
| 401 | Missing or invalid JWT token |
| 403 | Valid token but wrong user_id |
| 404 | Task not found or doesn't belong to user |
| 422 | Validation error (Pydantic rejects input) |
| 500 | Unexpected server error |

---

## Request/Response Flow

```
Client Request
     │
     ▼
┌─────────────────────┐
│   CORS Middleware    │ ← Check origin
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Route Handler     │ ← Match method + path
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  JWT Auth Dependency │ ← Verify token → 401 if invalid
│  (get_current_user)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  enforce_user_access │ ← Match user_id → 403 if mismatch
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Pydantic Validation │ ← Validate body → 422 if invalid
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Service Layer      │ ← Business logic
│  (task_service.py)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   SQLModel + Neon    │ ← DB query
│   (get_session)      │
└──────────┬──────────┘
           │
           ▼
     JSON Response
```

---

## Dependencies (pyproject.toml)

```toml
[project]
name = "todo-backend"
version = "1.0.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlmodel>=0.0.22",
    "pyjwt[crypto]>=2.9.0",
    "psycopg2-binary>=2.9.9",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]
```

---

## Running the Backend

```bash
cd backend

# Install dependencies
uv sync  # or pip install -e ".[dev]"

# Set environment variables
cp .env.example .env
# Edit .env with your Neon URL, secret, etc.

# Run dev server
uvicorn app.main:app --reload --port 8000

# Run with env file loaded
# If using python-dotenv, it auto-loads .env
```

### .env.example
```
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/todo_db?sslmode=require
BETTER_AUTH_SECRET=your-shared-secret-minimum-32-characters
CORS_ORIGINS=http://localhost:3000
```

---

## API Documentation

FastAPI auto-generates docs:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## Key Conventions

1. **Thin routes**: Route handlers only validate, delegate to services, and return responses
2. **Service layer**: All business logic and DB queries in `services/`
3. **Dependency injection**: Use `Depends()` for session, auth, and other shared logic
4. **Pydantic models**: Separate schemas for Create, Update, and Response — never expose the DB model directly
5. **User isolation**: Every service function takes `user_id` and filters all queries by it
6. **Async handlers**: Use `async def` for route handlers
7. **Type hints everywhere**: All function signatures fully typed
8. **No hardcoded values**: All config from environment variables

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| CORS blocked | Frontend origin not in CORS_ORIGINS | Add `http://localhost:3000` to CORS_ORIGINS |
| 422 on POST | Request body doesn't match Pydantic schema | Check field names, types, required vs optional |
| 404 on valid task | Query not filtering by user_id | Ensure service uses `where(Task.user_id == user_id)` |
| Import errors | Circular imports between models/routes | Import inside functions or restructure |
| Neon timeout | Serverless cold start | `pool_pre_ping=True` in engine config |
| `async` issues with SQLModel | SQLModel Session is sync | Use sync `Session`, async route handlers still work |
| Multiple validation errors | Pydantic V2 strict mode | Check `Field()` constraints match input |
