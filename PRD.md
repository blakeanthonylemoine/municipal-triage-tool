# Municipal Triage Tool PRD

## 1. Objective & Scope

**Problem:** Small, rural municipal and operations teams are overwhelmed by unstructured public intake (emails, web forms) that must be manually read, categorized, prioritized, and entered into legacy databases. They lack the budget for enterprise gov-tech platforms and the IT resources to manage bespoke integrations with their on-premise systems.

**Solution:** A lightweight, intelligent middleware layer that sits between the citizen and the clerk. It ingests unstructured requests, extracts critical metadata via AI, drafts responses, and provides a "Trust Layer" operator dashboard for one-click verification. Crucially, it relies on zero-integration outputs (like cleanly formatted auto-forwarded emails) to bypass legacy IT bottlenecks.

**Pricing Strategy:** A flat ~$299/month, explicitly priced below standard municipal discretionary spending limits to allow for credit-card purchases without requiring a city council board vote.

**Target Audience:** Rural county/parish clerks, municipal operations managers, and small public utility districts (starting with a pilot in a Louisiana parish).

## 2. Distribution & Onboarding

**Acquisition Channels:** State municipal association conferences (e.g., Police Jury Association of Louisiana), clerk listservs, Facebook groups, and word-of-mouth.

**Onboarding:** A self-serve UI that generates a pre-written, technical "1-pager" email template. The clerk forwards this to their IT department to request a simple auto-forwarding rule, while providing concrete answers about data residency, FOIA compliance, and privacy.

## 3. MVP Feature Requirements

| Feature | Description | Success Metric |
|---|---|---|
| Ingestion Pipeline | A webhook endpoint that accepts unstructured, forwarded email text payloads. | Correctly parses POST bodies without dropping requests. |
| ML Triage Engine | Gemini 3.5 Flash prompt pipeline extracting a strict Pydantic JSON object from text. | Categorization, Urgency (1–5), and Location extracted flawlessly. |
| Safety Flagging (no auto-response) | No automated receipt or reply is ever sent to a citizen without clerk review. AI flags life-safety issues internally for the clerk only. | Zero unconditional/automatic outbound messages of any kind; zero auto-routing to emergency services. |
| Triage Dashboard (Trust Layer) | Simple, web-based internal UI showing a side-by-side comparison of raw text vs. AI analysis. | Operator can seamlessly edit/verify AI deductions and click "Approve". |
| Zero-Integration Output Adapter | Output engine formatting approved data to bypass custom IT consulting. | Successfully generates perfectly structured system emails or standard CSVs for legacy DB entry. |
| FOIA & Compliance Tooling | Built-in data handling for public records requests and municipal retention policies. | One-click CSV export of tickets; background cron jobs that automatically purge data past retention limits. |

## 4. Out of Scope for MVP

- Individual per-clerk user accounts: each tenant (municipality) gets one shared login for now, not separate accounts per staff member.
- Self-serve tenant signup: new tenants are provisioned manually by the admin during onboarding; a self-serve flow is a likely future evolution as the customer count grows, so provisioning logic is being built as reusable rather than one-off.
- Automatic execution without human review: The "Trust Layer" UI is mandatory for early adoption and legal safety.
- Complex graphical data reporting: No analytics charts or advanced data visualization yet.

**Revised 2026-07-17:** the original MVP scope excluded full authentication entirely ("hardcode one admin user profile"). That's been superseded — real multi-tenant growth is the actual goal, not a single permanent pilot, so tenant-level authentication (one shared login per municipality, JWT bearer tokens) is now in scope for the Trust Layer UI. See `TASKS.md` Phase 2 for the detailed design.

**Revised 2026-07-17:** dropped the unconditional auto-responder / hardcoded 911 disclaimer entirely, not just its automation — no automatic email of any kind goes to a citizen before a clerk reviews it. Blake's read: this was an overly safety-focused idea that likely doesn't match how these municipalities' systems and liability processes currently work, and he's validating with prospective customers before reconsidering it. The Trust Layer's human-approval gate is now the *only* safety mechanism for outbound citizen communication — see the Citizen Notification design in `TASKS.md` Phase 3 for what replaces it (the AI-drafted response is emailed to the citizen only after a clerk approves the ticket, not automatically on intake).

## 5. The Moat & Defensibility

The defensibility of the product is not software integration; it is trust, niche focus, and rigorous empirical validation.

- **Proprietary Evaluation Dataset:** We will build and curate a labeled evaluation set of thousands of real, ground-truth municipal emails (including split-ticket cases, local addresses, and edge-case complaints) generated from our pilot programs.
- **Empirical Testing Architecture:** We will continuously run empirical experiments against this proprietary dataset to test the cognitive boundaries, consistency, semantic framing, and multimodal perceptual limits of our AI pipeline. This ensures our civic routing is mathematically more reliable than a generic CRM's AI bolt-on, creating an accumulating technical advantage that incumbents will not bother to build for small parishes.

## High Value User Stories

### 1. Core Workflow & Time Savings

- As an operations dispatcher, I want the system to automatically categorize incoming, unstructured emails (e.g., "Sanitation," "Public Works," "Permitting"), so that I don't have to spend the first two hours of my day reading and manually sorting every message.
- As a public works coordinator, I want the system to accurately extract the physical street address or cross-streets from a rambling, poorly spelled citizen email, so that my crews know exactly where to go without me having to decipher the text.

### 2. The "Trust Layer" & Control

- As a county clerk, I want to review the AI's suggested routing and drafted response on a simple dashboard before anything is executed, so that I maintain absolute quality control and ensure citizens never receive a hallucinated AI response.
- As a triage worker, I want the system to flag emails that contain multiple distinct issues (e.g., "a tree fell and broke a water pipe"), so that I can easily approve splitting the request into two separate tickets for Forestry and Water without duplicating my data entry.

### 3. Risk Mitigation & Public Safety

- As a municipal department head, I want high-urgency keywords (like "gas leak," "downed power line," or "flooding") to instantly trigger an emergency SMS or Slack alert to my on-call staff, so that we bypass the standard email queue and respond to public safety hazards immediately.

### 4. Legacy Integration (The Buyer's Moat)

- As a city manager with a tiny IT budget, I want this tool to plug directly into our existing public help@city.gov inbox, so that we don't have to retrain citizens on how to contact us or launch an expensive new web portal.
- As an administrative assistant, I want the approved ticket to automatically format and push directly into our existing, 10-year-old bespoke ticketing database, so that I don't have to copy-paste data between two different software screens.

### 5. Citizen Experience

- As a citizen reporting an issue, I want to receive an immediate, context-aware email acknowledging my specific problem (not just a generic "we received your email" auto-reply) along with an expected timeline, so that I feel heard and don't call the mayor's office to complain tomorrow.
