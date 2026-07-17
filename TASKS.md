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
- [x] Build Queue Component: `TicketQueue.tsx` fetches/renders pending tickets scoped to the authenticated tenant via `tenantApi` — the `CURRENT_TENANT_ID = 1` hardcode is gone. Verified against two real tenants: City of Rivergate (4 tickets) and the new Town of Ashcombe test account (0 tickets, confirms the empty-queue state and tenant isolation both render correctly).
- [x] Build Detail View: inline split-pane (`TicketDetail.tsx`), raw citizen text on the left, editable AI deductions (category, urgency, location, email, phone, drafted response) on the right. Verified via headless-browser screenshot — clicking a ticket opens the panel prefilled with its data.
  - [x] Backend: `GET /api/tenants/{tenant_id}/categories` lists a tenant's categories for the dropdown.
  - [x] Backend: `PATCH /api/tickets/{ticket_id}/approve` persists edited fields and sets status.
- [x] Wire Up Action Buttons: "Approve" button calls the PATCH endpoint with edited fields and sets `status` to `APPROVED`; verified end-to-end (ticket disappeared from the pending queue after approval).
- [x] [NEW — scope expansion] Admin Authentication + Tenant Management (built 2026-07-17, ahead of tenant-facing login, since tenants are provisioned by the admin): built within the existing React app, not sqladmin (supersedes Phase 4's original sqladmin plan — see note there). Shared JWT infra in `auth.py` (`create_access_token`/`decode_access_token`/`require_admin`) is deliberately principal-agnostic so tenant login can reuse it.
  - [x] Backend: `Tenant` gets `login_email` + `hashed_password` columns (migration `8d08955dbadf`), plus `tenant_service.py` (`provision_tenant`/`reset_tenant_credentials`) written as reusable functions, not inlined, so a future self-serve signup can call the same logic.
  - [x] Backend: `POST /api/admin/login` (single admin, credentials from `ADMIN_EMAIL`/`ADMIN_PASSWORD_HASH` env vars, set via `set_admin_credentials.py` which you run yourself — the password never passed through chat). Returns a JWT with `role: admin`.
  - [x] Backend: `GET/POST /api/admin/tenants` and `PATCH /api/admin/tenants/{id}/credentials`, all behind `require_admin`. List includes per-tenant ticket counts and token usage (the first real dashboard data).
  - [x] Frontend: `/admin/login` and `/admin` (route-guarded, redirects to login if unauthenticated), tenant table with create-tenant and reset-credentials forms, summary tiles (tenant count, pending tickets, tokens used). Verified via headless browser: unauthenticated redirect works, wrong-password error path works. Full successful-login flow needs your own manual check since only you hold the password.
- [x] Tenant-facing login (clerks) (built 2026-07-17): `POST /api/tenant/login` reuses the same JWT helpers with a tenant-scoped token (`role: tenant`, `sub: tenant_id`). New `require_tenant` dependency in `auth.py` derives `tenant_id` from the token — the old `GET /api/tenants/{id}/tickets/pending` and `GET /api/tenants/{id}/categories` routes were replaced with `GET /api/tickets/pending` and `GET /api/categories` (no tenant_id in the URL at all now), and `PATCH /api/tickets/{id}/approve` now scopes its lookup to the authenticated tenant so one municipality can't touch another's ticket by guessing an id. Frontend: `/login` page, `tenantAuth.ts`/`tenantApi.ts` (mirroring the admin pattern), `TicketQueue.tsx`/`TicketDetail.tsx` retrofitted onto `tenantApi` instead of raw hardcoded-URL axios calls (also closes the "unify frontend API client" design-review item below), route guard on `/` redirecting to `/login`, logout button. Verified end-to-end in a real browser with real tenant credentials (City of Rivergate): wrong password rejected, correct login shows the real pending queue, detail view still works, logout + revisit redirects back to login.
  - [x] Note: the ingestion webhook (`POST /webhook/{tenant_id}`) is hit by an automated email-forwarding system, not a logged-in clerk — it stays outside this JWT login system, unchanged. It'll need its own protection story (e.g. a per-tenant shared secret) later; still not scoped.
- [x] [NEW] Build FOIA Export Tool (built 2026-07-17): `GET /api/tickets/export` streams a CSV of all of the authenticated tenant's tickets (id, status, date, category, urgency, location, email, phone, original complaint, drafted response, safety flag). Deliberately kept low-profile in the UI per Blake's call — tucked behind a small "Tools" dropdown in the queue header rather than a prominent button, since it's expected to be a rare action. Verified end-to-end: logged in, opened Tools, downloaded a real CSV, confirmed the header row, correct row count, and real ticket content; also tested cross-tenant isolation in pytest (one tenant's export never contains another tenant's data).

### Design Review Follow-ups (2026-07-17)

From a design review of the backend and frontend as built so far. All gate Phase 3 — none of Phase 3 starts until these are resolved, in this priority order:

- [x] [SECURITY, top priority] Auth-gate the unauthenticated tenant-facing endpoints (closed 2026-07-17): resolved by building full tenant login rather than a stopgap — see "Tenant-facing login" above. All three routes now require a valid tenant JWT and are scoped to the token's tenant_id; cross-tenant access is tested (`test_cannot_approve_another_tenants_ticket`, `test_categories_do_not_leak_across_tenants`).
- [x] Fix the webhook's hardcoded category list (closed 2026-07-17): `ticket_service._categories_prompt_string` now queries the tenant's real categories and builds the prompt string dynamically. Verified two ways: a mocked pytest asserting the exact tenant category id/name appears in the prompt sent to Gemini (`test_receive_webhook_creates_ticket_using_tenants_real_categories`), and a live webhook call against the real Gemini API that correctly categorized a new complaint.
- [x] Resolve the two overlapping ticket-ingestion endpoints (closed 2026-07-17): `POST /api/v1/intake/{tenant_id}` was dead code from before the AI pipeline existed — removed. Its one useful behavior (404 if the tenant doesn't exist) was folded into `/webhook/{tenant_id}`, which never had that check before. There's now exactly one ingestion endpoint.
- [x] Split `main.py` into `APIRouter`s by domain (closed 2026-07-17): `routers/tickets.py`, `routers/admin.py`, `routers/webhook.py`. `main.py` is now ~18 lines — just app setup, CORS, and `include_router` calls.
- [x] Extract ticket creation/approval logic into a service module (closed 2026-07-17): `ticket_service.py` (`create_ticket_from_webhook`, `approve_ticket`, `export_tickets_csv`), mirroring `tenant_service.py`. This is also where the hardcoded-categories fix above lives.
- [x] Add Pydantic `response_model` schemas (closed 2026-07-17): new `schemas.py` (`TenantOut`, `TicketOut`, `CategoryOut`, `TokenResponse`, plus the existing request models). `hashed_password` can no longer leak by omission — it's structurally not a field on `TenantOut`, not something a route handler has to remember to exclude.
- [x] Centralize config (closed 2026-07-17): new `config.py` using pydantic-settings, one `settings` singleton loaded once. `database.py`, `ai_pipeline.py`, `auth.py`, and the routers all import from it instead of scattering `os.getenv`/`load_dotenv()` calls.
- [x] Unify the frontend API-calling pattern (closed 2026-07-17 as part of tenant login): `TicketQueue.tsx`/`TicketDetail.tsx` now go through `tenantApi.ts` (mirroring `adminApi.ts` — base URL, auth header, 401 handling in one place) instead of raw hardcoded-URL `axios` calls.
- [x] Add shared TypeScript types (closed 2026-07-17): new `types.ts` (`Ticket`, `Category`, `TenantSummary`), replacing `TicketQueue.tsx`'s untyped `any[]` and the slightly-different local interfaces that had been redefined per-file.

**All design review follow-ups are closed as of 2026-07-17.** Phase 3 is unblocked. Full backend suite (28 tests) passes, frontend typechecks clean, and the refactor was verified end-to-end in a real browser (tenant login → queue → detail view → approve, plus a live webhook call proving the dynamic categories fix) rather than just by tests passing.

## Phase 3: Middleware Execution & Pilot Prep

- [ ] [NEW] Implement Unconditional Auto-Responder: Wire the ingestion route to immediately fire back a receipt email containing the hardcoded 911 liability disclaimer.
- [ ] Build Output Adapter: Write the script that takes an "Approved" ticket and formats it into a clean, zero-integration email to send back to the clerk's existing inbox.
- [ ] [NEW] IT Onboarding Generator: Build the self-serve step that hands the clerk the technical 1-pager to give their IT department.
- [ ] Simulate End-to-End Flow: Run mock email data through the entire pipeline to confirm the dashboard behaves predictably under load.
- [ ] Deploy Stable Alpha: Move the application from your laptop to a live free-tier hosting platform to prepare for live integration testing in Louisiana.

## Phase 4: System Administration & Compliance

- [x] Build the Global Admin Dashboard: superseded by the Phase 2 Admin Authentication + Tenant Management work above — built as a custom React admin panel (login, tenant CRUD, token/ticket summary) instead of sqladmin, so it shares styling and infra with the rest of the app. More admin functionality (deeper monitoring/debugging views) still to come as needs surface.
- [ ] [NEW] Automated Retention Cron Job: Script a background task that hard-deletes ticket data older than the municipality's legal retention schedule.

## Phase 5: The Moat (Empirical Testing)

- [ ] [NEW] Evaluation Dataset Architecture: Set up a secure, isolated database table to capture split-ticket cases and ground-truth pilot data, establishing the regression-testing loop for the AI pipeline.
