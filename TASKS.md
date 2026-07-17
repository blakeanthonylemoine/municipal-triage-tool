# Project Task Tracker

## Phase 1: Core Engine & Data Persistence (Completed)

- [x] Define Database Schema: Create PostgreSQL models for Tickets (storing raw data, metadata, status, and system logs).
- [x] Build FastAPI Ingestion: Write the webhook receiver route that captures payloads and commits raw text to the database.
- [x] Implement LLM Integration: Write the service class connecting FastAPI to Gemini 3.5 Flash via standard prompt templates.
- [x] Test JSON Enforcement: Verify the AI consistently outputs the target Pydantic data structures without syntax failures.

## Phase 2: The Trust Layer UI (In Progress)

Scoped in detail during the 2026-07-17 design session. Layout is a single-page master/detail (no router yet); Approve is full edit-then-approve; tenant auth is a formal, deliberate expansion beyond the original MVP's "hardcode one admin" note, not a stopgap.

- [x] Initialize Frontend Framework: Vite + React 19 + TypeScript + Tailwind v4 already set up correctly in `frontend/`.
- [x] Clean up stray root-level npm artifacts: a duplicate `package.json`/`package-lock.json`/`node_modules` had been created at the project root by mistake; removed, `frontend/`'s install is the only one now.
- [x] Wire `App.tsx` to actually render the dashboard: added a header and mounted `TicketQueue`, replacing the "Tailwind is working" placeholder. Verified in a real headless-browser screenshot against the live backend (tenant 1's queue renders tickets #10 and #13).
- [ ] Build Queue Component: `TicketQueue.tsx` already fetches/renders pending tickets; still needs to switch from the hardcoded `CURRENT_TENANT_ID = 1` to the authenticated tenant (see Tenant Authentication below).
- [x] Build Detail View: inline split-pane (`TicketDetail.tsx`), raw citizen text on the left, editable AI deductions (category, urgency, location, email, phone, drafted response) on the right. Verified via headless-browser screenshot — clicking a ticket opens the panel prefilled with its data.
  - [x] Backend: `GET /api/tenants/{tenant_id}/categories` lists a tenant's categories for the dropdown.
  - [x] Backend: `PATCH /api/tickets/{ticket_id}/approve` persists edited fields and sets status.
- [x] Wire Up Action Buttons: "Approve" button calls the PATCH endpoint with edited fields and sets `status` to `APPROVED`; verified end-to-end (ticket disappeared from the pending queue after approval).
- [ ] [NEW — scope expansion] Tenant Authentication: originally the PRD scoped this out of MVP ("hardcode one admin"), but we're pulling it in now since multi-tenant growth is the actual goal, not just a single pilot. Design:
  - [ ] One shared login per tenant (a municipality-level credential, not individual per-clerk accounts — that can come later if needed).
  - [ ] JWT bearer tokens: `POST /api/auth/login` (tenant email + password) returns a JWT; frontend attaches it as an `Authorization` header on subsequent calls.
  - [ ] Backend: add login credential fields to `Tenant` (email + hashed password) plus an Alembic migration.
  - [ ] Backend: auth dependency that derives `tenant_id` from the verified JWT rather than trusting a URL path segment, and protects the dashboard/API routes (queue, categories, ticket PATCH).
  - [ ] Backend: manual provisioning path for now (you create each tenant + credentials by hand during onboarding) — written as a reusable function/service, not inlined into a script, so a future self-serve signup endpoint can call the same logic without a rewrite.
  - [ ] Frontend: login screen, token storage + axios interceptor, redirect-to-login when unauthenticated.
  - [ ] Note: the ingestion webhook (`POST /webhook/{tenant_id}`) is hit by an automated email-forwarding system, not a logged-in clerk — it stays outside this JWT login system. It'll need its own protection story (e.g. a per-tenant shared secret) later; not scoped here.
- [ ] [NEW] Build FOIA Export Tool: Add a one-click global CSV export button to the UI so clerks can instantly comply with public records requests.

## Phase 3: Middleware Execution & Pilot Prep

- [ ] [NEW] Implement Unconditional Auto-Responder: Wire the ingestion route to immediately fire back a receipt email containing the hardcoded 911 liability disclaimer.
- [ ] Build Output Adapter: Write the script that takes an "Approved" ticket and formats it into a clean, zero-integration email to send back to the clerk's existing inbox.
- [ ] [NEW] IT Onboarding Generator: Build the self-serve step that hands the clerk the technical 1-pager to give their IT department.
- [ ] Simulate End-to-End Flow: Run mock email data through the entire pipeline to confirm the dashboard behaves predictably under load.
- [ ] Deploy Stable Alpha: Move the application from your laptop to a live free-tier hosting platform to prepare for live integration testing in Louisiana.

## Phase 4: System Administration & Compliance

- [ ] Build the Global Admin Dashboard: Implement sqladmin for monitoring token usage, tenant management, and debugging.
- [ ] [NEW] Automated Retention Cron Job: Script a background task that hard-deletes ticket data older than the municipality's legal retention schedule.

## Phase 5: The Moat (Empirical Testing)

- [ ] [NEW] Evaluation Dataset Architecture: Set up a secure, isolated database table to capture split-ticket cases and ground-truth pilot data, establishing the regression-testing loop for the AI pipeline.
