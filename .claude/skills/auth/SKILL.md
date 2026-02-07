---
name: auth
description: Better Auth + JWT authentication patterns — signup/signin flows, JWT verification, protected routes, and cross-service auth between Next.js frontend and FastAPI backend.
---

# Auth Skill — Better Auth + JWT Integration

## Overview
This skill provides the complete authentication implementation pattern for a Full-Stack monorepo with **Next.js 16+ frontend** and **Python FastAPI backend**, using **Better Auth** with **JWT plugin** for cross-service authentication against **Neon Serverless PostgreSQL**.

---

## Architecture

```
┌─────────────────────────────┐            ┌─────────────────────────────┐
│       Next.js Frontend      │            │       FastAPI Backend        │
│                             │            │                             │
│  Better Auth (Server)       │            │  JWT Middleware (PyJWT)      │
│  ├── JWT Plugin enabled     │            │  ├── Extract Bearer token   │
│  ├── Manages user table     │            │  ├── Verify with shared     │
│  ├── Handles signup/signin  │            │  │   BETTER_AUTH_SECRET     │
│  └── Issues JWT on login    │            │  ├── Decode sub, email      │
│                             │            │  └── Enforce user_id match  │
│  Better Auth Client         │            │                             │
│  ├── jwtClient plugin       │            │  Protected Routes           │
│  ├── signUp / signIn        │  JWT in    │  ├── 401 if no/bad token   │
│  ├── getToken()  ──────────────Bearer──▶ │  ├── 403 if user mismatch  │
│  ├── signOut                │  Header    │  └── Filter data by user   │
│  └── getSession             │            │                             │
└─────────────────────────────┘            └─────────────────────────────┘
              │                                         │
              │          BETTER_AUTH_SECRET              │
              └──────────── (shared) ───────────────────┘
```

---

## Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `BETTER_AUTH_SECRET` | Frontend + Backend | Shared secret for JWT signing/verification. Min 32 chars. |
| `DATABASE_URL` | Frontend (Better Auth) + Backend | Neon PostgreSQL connection string with `?sslmode=require` |
| `NEXT_PUBLIC_API_URL` | Frontend | Backend base URL (e.g., `http://localhost:8000`) |
| `NEXT_PUBLIC_BETTER_AUTH_URL` | Frontend | Better Auth base URL (e.g., `http://localhost:3000`) |
| `CORS_ORIGINS` | Backend | Allowed frontend origin (e.g., `http://localhost:3000`) |

**Critical**: `BETTER_AUTH_SECRET` must be **identical** on both frontend and backend. Generate with:
```bash
openssl rand -base64 32
```

---

## Frontend Implementation (Next.js 16+)

### 1. Install Dependencies
```bash
cd frontend
npm install better-auth
```

### 2. Better Auth Server Config
**File**: `frontend/src/lib/auth.ts`
```typescript
import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

export const auth = betterAuth({
  database: new Pool({
    connectionString: process.env.DATABASE_URL,
  }),
  plugins: [jwt()],
  secret: process.env.BETTER_AUTH_SECRET,
  emailAndPassword: {
    enabled: true,
  },
});
```

### 3. Better Auth API Route Handler
**File**: `frontend/src/app/api/auth/[...all]/route.ts`
```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

### 4. Auth Client
**File**: `frontend/src/lib/auth-client.ts`
```typescript
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
  plugins: [jwtClient()],
});
```

### 5. Auth Hook
**File**: `frontend/src/hooks/useAuth.ts`
```typescript
"use client";
import { authClient } from "@/lib/auth-client";

export function useAuth() {
  const session = authClient.useSession();

  const signUp = async (email: string, password: string, name: string) => {
    return await authClient.signUp.email({ email, password, name });
  };

  const signIn = async (email: string, password: string) => {
    return await authClient.signIn.email({ email, password });
  };

  const signOut = async () => {
    return await authClient.signOut();
  };

  const getToken = async (): Promise<string | null> => {
    const tokenResponse = await authClient.getToken();
    return tokenResponse?.token ?? null;
  };

  return {
    session: session.data,
    isLoading: session.isPending,
    isAuthenticated: !!session.data,
    signUp,
    signIn,
    signOut,
    getToken,
  };
}
```

### 6. API Client with JWT
**File**: `frontend/src/lib/api.ts`
```typescript
import { authClient } from "./auth-client";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchWithAuth(path: string, options: RequestInit = {}) {
  const tokenResponse = await authClient.getToken();
  const token = tokenResponse?.token;

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (response.status === 401) {
    // Token expired or invalid — redirect to login
    window.location.href = "/login";
    throw new Error("Authentication expired");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `API error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  getTasks: (userId: string) => fetchWithAuth(`/api/${userId}/tasks`),
  getTask: (userId: string, taskId: number) => fetchWithAuth(`/api/${userId}/tasks/${taskId}`),
  createTask: (userId: string, data: { title: string; description?: string }) =>
    fetchWithAuth(`/api/${userId}/tasks`, { method: "POST", body: JSON.stringify(data) }),
  updateTask: (userId: string, taskId: number, data: { title?: string; description?: string }) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteTask: (userId: string, taskId: number) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}`, { method: "DELETE" }),
  toggleComplete: (userId: string, taskId: number) =>
    fetchWithAuth(`/api/${userId}/tasks/${taskId}/complete`, { method: "PATCH" }),
};
```

### 7. Protected Route Layout
**File**: `frontend/src/app/dashboard/layout.tsx`
```typescript
"use client";
import { useAuth } from "@/hooks/useAuth";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return null;

  return <>{children}</>;
}
```

---

## Backend Implementation (FastAPI)

### 1. Install Dependencies
```bash
cd backend
pip install pyjwt[crypto] fastapi uvicorn
```
Or in `pyproject.toml`:
```toml
dependencies = ["fastapi", "uvicorn", "sqlmodel", "pyjwt[crypto]"]
```

### 2. JWT Verification Middleware
**File**: `backend/app/middleware/auth.py`
```python
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()
BETTER_AUTH_SECRET = os.environ["BETTER_AUTH_SECRET"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Verify JWT token and return user payload."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, BETTER_AUTH_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity",
            )
        return {
            "user_id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name"),
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )


def enforce_user_access(user_id: str, current_user: dict) -> None:
    """Ensure the authenticated user matches the requested user_id."""
    if current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
```

### 3. Using in Route Handlers
**File**: `backend/app/routes/tasks.py`
```python
from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user, enforce_user_access

router = APIRouter(prefix="/api/{user_id}/tasks")


@router.get("")
async def list_tasks(user_id: str, current_user: dict = Depends(get_current_user)):
    enforce_user_access(user_id, current_user)
    # ... query tasks filtered by user_id
```

### 4. CORS Configuration
**File**: `backend/app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Todo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## User Table (Managed by Better Auth)

Better Auth auto-creates and manages the `user` table in Neon. The backend reads from it but **never writes** to it. Schema:

| Column | Type | Notes |
|--------|------|-------|
| id | text | Primary key, generated by Better Auth |
| email | text | Unique |
| name | text | From signup |
| emailVerified | boolean | |
| image | text | Optional |
| createdAt | timestamp | |
| updatedAt | timestamp | |

Better Auth also creates `session` and `account` tables automatically.

---

## Security Checklist

- [ ] `BETTER_AUTH_SECRET` is 32+ characters
- [ ] Same secret on frontend and backend
- [ ] Secret in `.env`, added to `.gitignore`
- [ ] JWT has expiry set
- [ ] All API endpoints use `get_current_user` dependency
- [ ] All routes call `enforce_user_access()`
- [ ] CORS allows only the frontend origin
- [ ] `sslmode=require` in DATABASE_URL for Neon
- [ ] No JWT stored in localStorage
- [ ] `.env.example` provided with placeholder values (no real secrets)

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 on all requests | Secret mismatch | Verify `BETTER_AUTH_SECRET` is identical on both sides |
| JWT decode fails | Wrong algorithm | Ensure both sides use `HS256` |
| CORS errors | Missing origin | Add frontend URL to `CORS_ORIGINS` |
| Token undefined on frontend | Plugin not configured | Ensure `jwtClient()` is in `createAuthClient` plugins |
| Neon connection timeout | Missing SSL | Add `?sslmode=require` to `DATABASE_URL` |
| 403 on valid requests | user_id mismatch | Ensure frontend sends correct user_id from session |

---

## Testing Auth

### Backend (pytest)
```python
import jwt, os

def make_token(user_id="test-user", expired=False):
    payload = {"sub": user_id, "email": "test@example.com"}
    if expired:
        payload["exp"] = 0  # already expired
    return jwt.encode(payload, os.environ.get("BETTER_AUTH_SECRET", "test-secret"), algorithm="HS256")

# Test: no token → 401
# Test: expired token → 401
# Test: invalid token → 401
# Test: valid token, wrong user_id in URL → 403
# Test: valid token, correct user_id → 200
```

### Frontend
- Mock `authClient.getToken()` in tests
- Verify `Authorization: Bearer <token>` header is attached
- Test redirect to `/login` when session is null
