---
id: PHR-007
title: Frontend Pages Specification
stage: spec
date: 2026-02-07
surface: agent
model: claude-opus-4-6
feature: 006-frontend-pages
branch: 006-frontend-pages
user: developer
command: /sp.specify
labels: [spec, frontend, pages, routing, auth-pages, dashboard]
links:
  spec: specs/006-frontend-pages/spec.md
  ticket: ""
  adr: ""
  pr: ""
files:
  - path: specs/006-frontend-pages/spec.md
    action: created
  - path: specs/006-frontend-pages/checklists/requirements.md
    action: created
tests:
  - none
---

## Prompt

/sp.specify Frontend Pages for Phase II Todo Full-Stack Web Application

This spec defines WHAT pages the frontend must have — their purpose, access rules, and what users see on each page.

Intent:
Define the pages of the Next.js 16+ App Router frontend — login, signup, and dashboard — with clear routing, access control, and content requirements.

Target Audience:
Frontend Agent (primary), Auth Agent, Testing Agent

Success Criteria (SMART):

Page 1 — Login (/login):
- Displays email and password input fields
- Submit button triggers Better Auth signin
- Invalid credentials show error message inline — no page reload
- Successful login redirects to /dashboard
- Link to /signup for new users ("Don't have an account? Sign up")
- Already authenticated users visiting /login are redirected to /dashboard
- Loading indicator shown during signin request

Page 2 — Signup (/signup):
- Displays name, email, and password input fields
- Submit button triggers Better Auth signup
- Duplicate email shows error message inline
- Empty required fields show validation errors
- Successful signup redirects to /dashboard (auto-login after signup)
- Link to /login for existing users ("Already have an account? Sign in")
- Already authenticated users visiting /signup are redirected to /dashboard
- Loading indicator shown during signup request

Page 3 — Dashboard (/dashboard):
- Protected route — unauthenticated users redirected to /login
- Displays the user's name or email in a header/navbar
- Contains logout button — clicking signs out and redirects to /login
- Shows the full task list (TaskList component)
- Contains "Add Task" form or button to open form (TaskForm component)
- Contains filter controls for status (all/pending/completed) and sort (created/title)
- Shows loading skeleton while tasks are being fetched
- Shows error message if task fetch fails
- Shows empty state message when user has no tasks

Page 4 — Root (/):
- Redirects to /dashboard if authenticated
- Redirects to /login if not authenticated

Constraints:
- Next.js 16+ App Router with /app directory
- Login and Signup are public routes — no auth required
- Dashboard is protected — auth required
- All pages use Tailwind CSS for styling
- No separate CSS files — Tailwind utility classes only
- Server components for layouts, client components for interactive forms
- All API calls through lib/api.ts — never direct fetch in pages

Non-Goals:
- No landing page or marketing page
- No settings/profile page
- No password reset page
- No email verification page
- No admin panel
- No dark mode toggle (use system default or single theme)

Dependencies:
- Architecture spec (frontend service boundary)
- Auth spec (Better Auth client, protected routes, session check)
- Task CRUD spec (what features dashboard must expose)
- Frontend Components spec will define the reusable components used in these pages
- This spec uses Frontend Agent with `.claude/skills/frontend/SKILL.md`

## Response snapshot

Created spec 006-frontend-pages with 7 user stories (4 P1, 3 P2), 39 functional requirements organized by page (Login: FR-001–010, Signup: FR-011–022, Dashboard: FR-023–034, Root: FR-035–036, Cross-Cutting: FR-037–039), 6 edge cases, 4 key entities, 5 assumptions, 4 dependencies, 6 non-goals, and 10 measurable success criteria. All checklist items pass. No clarifications needed — user input was comprehensive.

## Outcome

- Impact: Created comprehensive frontend pages spec covering all 4 routes with access control, content requirements, and user flows
- Tests: No tests at spec stage
- Files: specs/006-frontend-pages/spec.md (created), specs/006-frontend-pages/checklists/requirements.md (created)
- Next prompts: /sp.plan for frontend-pages, or create additional specs (e.g., Frontend Components)
- Reflection: User input was thorough — no clarifications needed. Spec maps cleanly to 4 distinct pages with clear boundaries.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Quality checklist — PASS (all items checked)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
