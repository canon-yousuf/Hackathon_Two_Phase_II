# Quickstart: Foundation Setup

## Prerequisites

- Python 3.13+ with `uv` package manager
- Node.js 20+ with `npm`
- Neon PostgreSQL database (free tier)
- Generate a shared secret: `openssl rand -base64 32`

## 1. Clone and Configure

```bash
# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit both files with your actual values:
# - DATABASE_URL: from Neon dashboard
# - BETTER_AUTH_SECRET: same 32+ char secret in BOTH files
```

## 2. Start Backend

```bash
cd backend
uv sync
uvicorn app.main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/health` → `{"status": "healthy"}`

## 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Verify: Open `http://localhost:3000` in browser.

## 4. Test Auth Flow

```bash
# Sign up a user
curl -X POST http://localhost:3000/api/auth/sign-up/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123", "name": "Test User"}'

# Sign in
curl -X POST http://localhost:3000/api/auth/sign-in/email \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpassword123"}'
```

## 5. Verify Database

Check Neon dashboard — you should see tables:
- `user` (created by Better Auth)
- `session` (created by Better Auth)
- `account` (created by Better Auth)
- `tasks` (created by SQLModel on backend startup)

## What's NOT Included Yet

- No task CRUD endpoints (just the `/health` endpoint)
- No frontend pages (login, signup, dashboard)
- No API client (`lib/api.ts`)
- No protected route middleware
