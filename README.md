# ViewBox Club — Respondent Management & Survey Operations Platform

Concave Insights Technical Assessment — Full Stack Developer (Python & React)

---

## 1. Project Overview

ViewBox Club is an integrated, full-stack respondent management and survey operations platform built for market research firm Concave Insights. The system automates dynamic source attribution tracking across 50+ channels, enforces deterministic 15-day survey lifecycles with strict/flexible eligibility criteria, orchestrates a three-stage referral verification workflow (`Lead` -> `Fit` -> `Completed`), provides a mobile-first respondent portal with masked privacy controls, and equips operations and administrators with real-time analytics, resilient CSV imports, and Meta lead integration.

---

## 2. Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, SQLite (development with WAL mode) / PostgreSQL-compatible schema, Pandas, OpenPyXL, Pytest, HTTPX.
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui component patterns, React Router v6, TanStack Query v5, React Hook Form, Zod, Recharts, Lucide React.
- **Architecture:** Modular monolith with strict layered separation (API Controllers -> Domain Services -> Repositories -> ORM Entities).

---

## 3. Setup and Run

### 3.1 Prerequisites
- Python 3.11+
- Node.js 18+ and npm 9+

### 3.2 Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed baseline demo data
alembic upgrade head
python ../scripts/seed_demo_data.py

# Launch FastAPI development server
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/docs`

### 3.3 Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```
Client application will be live at: `http://localhost:5173`

---

## 4. Demo Logins and Test Data

The platform features passwordless mock OTP authentication. In development mode, the OTP is displayed directly on-screen or returned by the login API:

| Role | Mobile Number | Mock OTP | Access Scope |
|---|---|---|---|
| **System Administrator** | `9999900001` | `123456` | Full system governance, source management, survey config, CSV import, BI analytics |
| **Operations Specialist** | `9999900002` | `123456` | Respondent triage, referral verification queue (`Fit`/`Completed`), payout review |
| **Respondent (Existing)** | `9876543210` | `123456` | Mobile-first portal, survey feed, eligibility explanations, masked referrals |
| **New Respondent** | Any 10-digit number | `123456` | Triggers first-time demographic onboarding flow |

---

## 5. Features Status Matrix

| Feature | Assessment Category | Status | Implementation Notes |
|---|---|---|---|
| **Dynamic Source Tracking** | Core Requirement | Completed (Design & Arch) | Tokenized URLs (`/join?source_token=...`), click logging, fallback dropdown |
| **Respondent Portal (Mobile-First)** | Core Requirement | Completed (Design & Arch) | Touch-optimized, mock OTP, survey feed, masked referrals (`98XXXXXX21`) |
| **Eligibility Engine** | Core Requirement | Completed (Design & Arch) | Strict vs Flexible rules, 15-day deadline, 3-month cool-off arithmetic, quota locks |
| **Referral Workflow** | Core Requirement | Completed (Design & Arch) | Three-stage state machine: `Lead` -> `Fit` -> `Completed` / `Failed` with reason |
| **Admin Panel & Data Grid** | Core Requirement | Completed (Design & Arch) | Debounced search, multi-filtering, CSV/XLSX export, source analytics |
| **Resilient CSV Import** | Core Requirement | Completed (Design & Arch) | 11-step pipeline, normalization (cities, dates, phones), preview & error report |
| **Meta Ads Lead Endpoint** | Core Requirement | Completed (Design & Arch) | `POST /api/v1/integrations/meta/leads`, campaign metadata, idempotent `leadgen_id` |
| **Fraud & Duplicate Detection** | Advanced Bonus | Completed (Design & Arch) | Quarantine review queue: duplicate phones, self-referrals, referral rings |
| **Payout Ledger** | Advanced Bonus | Completed (Design & Arch) | Two-step authorization: survey completion rewards & referral bonuses |

---

## 6. Database Design

The relational database architecture is modeled in Third Normal Form (3NF) across 19 distinct tables ensuring data integrity, strict referential constraints, and zero redundancy.

Comprehensive documentation and visual diagrams are located in the `/design` directory:
- [design/database_schema.md](file:///c:/Users/Runmay%20Shirsat/OneDrive/Desktop/ViewBox-Panel-System/design/database_schema.md) — Detailed table dictionary, constraints, indexes.
- [design/er_diagram.png](file:///c:/Users/Runmay%20Shirsat/OneDrive/Desktop/ViewBox-Panel-System/design/er_diagram.png) — High-resolution entity-relationship diagram.
- [design/architecture.md](file:///c:/Users/Runmay%20Shirsat/OneDrive/Desktop/ViewBox-Panel-System/design/architecture.md) — Modular monolith system architecture.
- [design/user_flow.md](file:///c:/Users/Runmay%20Shirsat/OneDrive/Desktop/ViewBox-Panel-System/design/user_flow.md) — Screen-by-screen journey mapping.
- [design/user_flow.png](file:///c:/Users/Runmay%20Shirsat/OneDrive/Desktop/ViewBox-Panel-System/design/user_flow.png) — Visual user journey swimlanes.

---

## 7. API Endpoints Overview

| Method | Endpoint | Purpose | Access Control |
|---|---|---|---|
| `POST` | `/api/v1/auth/otp/send` | Request 6-digit mock OTP for mobile number | Public |
| `POST` | `/api/v1/auth/otp/verify` | Verify OTP and receive JWT access/refresh token | Public |
| `GET` | `/api/v1/members/me` | Fetch authenticated respondent profile | Respondent |
| `POST` | `/api/v1/members/onboarding` | Complete first-time demographic onboarding | Respondent |
| `GET` | `/api/v1/surveys/feed` | List active surveys with member eligibility status | Respondent |
| `POST` | `/api/v1/surveys/{id}/apply` | Submit survey application with atomic quota reservation | Respondent |
| `GET` | `/api/v1/referrals/my-referrals` | List referred members with phone numbers masked (`98XXXXXX21`) | Respondent |
| `GET` | `/api/v1/operations/queue` | Retrieve pending respondent & referral verification queues | Operations, Admin |
| `PATCH` | `/api/v1/operations/referrals/{id}/stage` | Update referral stage (`Fit`, `Completed`, `Failed`) with reason | Operations, Admin |
| `POST` | `/api/v1/operations/payouts/{id}/approve` | Sign off on owed survey reward or referral bonus | Operations, Admin |
| `GET` | `/api/v1/admin/respondents` | Searchable, paginated respondent data grid | Admin |
| `GET` | `/api/v1/admin/respondents/export` | Download filtered dataset as `.csv` or `.xlsx` | Admin |
| `POST` | `/api/v1/admin/sources` | Create new dynamic acquisition source and tokenized URL | Admin |
| `POST` | `/api/v1/admin/imports/upload` | Upload messy CSV for normalization & error preview | Admin |
| `POST` | `/api/v1/admin/imports/{id}/commit` | Atomically commit valid rows to database | Admin |
| `POST` | `/api/v1/integrations/meta/leads` | Ingest Meta Lead Ads webhook with campaign metadata | Public / API Key |

---

## 8. Assumptions and Architectural Decisions

### Decision 1: Source Conflict (Channel Link vs Referral Member)
- **Question:** If a person registers via an Instagram link but types an existing member's referral code, who gets credit?
- **Decision:** **Both are preserved independently.** The channel acquisition source is recorded as `Instagram` (for channel ROI attribution), and the referral relationship is created linking the referring member to the candidate (for bonus eligibility). They represent orthogonal business dimensions.

### Decision 2: First-Touch vs Last-Touch Attribution
- **Question:** If someone clicks a WhatsApp group link on Day 1, does not register, and returns on Day 7 via an Instagram post and registers, which source gets credit?
- **Decision:** **First-touch is primary; subsequent touches are logged as attribution events.** The member's primary acquisition source is stored as `WhatsApp Group - Mumbai`, while an `AttributionEvent` is logged for both interactions.

### Decision 3: Payment Gateway Sandbox & Disbursement Blueprint
- **Question:** How would a live payment gateway be integrated?
- **Decision:** RazorpayX or Cashfree Payouts API integration. The system implements a strict two-stage process: (1) Ops team reviews quality and approves the payout record; (2) Worker dispatches a payout transfer request (`POST /v1/payouts`) with idempotency key. Payout status moves from `PENDING_APPROVAL` -> `APPROVED` -> `PROCESSING` -> `PAID`. Failed webhooks transition status to `FAILED` with provider error code without blocking respondent access.

### Decision 4: Cool-Off Arithmetic & Leap Years
- **Decision:** Survey cool-off adds 3 full calendar months using Python `relativedelta(months=+3)`. If a survey was completed on Nov 30, the next eligible date is Mar 1 (clamped past the end of February).

---

## 9. Known Issues and Next Steps

- **MVP SMS Provider:** Production deployment will replace mock OTP with Twilio / Gupshup SMS gateway.
- **Automated Fraud Graph:** Future milestone will implement automated graph traversal for detecting complex referral rings ($A \rightarrow B \rightarrow C \rightarrow A$).
