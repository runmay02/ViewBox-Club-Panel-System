# ViewBox Club — Technical Architecture Document
**Concave Insights — Technical Assessment: Full Stack Developer (Python/React)**

---

## 1. Architectural Philosophy & Principles

The ViewBox Panel System is architected as a **Modular Monolith**. This pattern delivers:
- **High Cohesion & Low Coupling:** Domain logic is organized into explicit functional services (Eligibility, Attribution, Referral, Ingestion, Payouts) without the operational overhead and network latency of microservices.
- **Strict Separation of Concerns:** Database interactions reside strictly in repositories; business rules live in domain services; API controllers remain thin orchestrators.
- **Single Source of Truth:** Business logic (especially survey eligibility math and referral state transitions) is authored exclusively in Python backend services and consumed by frontend clients via typed API contracts.
- **Portability & Determinism:** Designed for seamless local execution using SQLite, while remaining fully compatible with production PostgreSQL deployments (using standard ANSI SQL, typed JSON columns, and UTC timestamps).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER                                    │
│   ┌───────────────────────────┐         ┌───────────────────────────────┐   │
│   │ Respondent Portal (Mobile)│         │ Admin & Ops Portals (Desktop) │   │
│   │ React 18 + Tailwind CSS   │         │ React 18 + TanStack + Recharts│   │
│   └─────────────┬─────────────┘         └───────────────┬───────────────┘   │
└─────────────────┼───────────────────────────────────────┼───────────────────┘
                  │ HTTPS / JSON REST API                 │
┌─────────────────▼───────────────────────────────────────▼───────────────────┐
│                           API GATEWAY / FASTAPI                             │
│  - CORS Middleware  - SlowAPI Rate Limiting  - Request ID Tracing           │
│  - JWT Bearer Authentication  - RBAC Route Guards (Admin/Ops/Respondent)   │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                           BUSINESS SERVICE LAYER                            │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  ┌─────────────┐ │
│  │   Eligibility Engine    │  │    Attribution Engine    │  │ Referral SM │ │
│  └─────────────────────────┘  └──────────────────────────┘  └─────────────┘ │
│  ┌─────────────────────────┐  ┌──────────────────────────┐  ┌─────────────┐ │
│  │  CSV Ingestion Pipeline │  │  Meta Leadgen Ingestion  │  │ Payout Svc  │ │
│  └─────────────────────────┘  └──────────────────────────┘  └─────────────┘ │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                    DATA ACCESS LAYER (SQLAlchemy 2.0 ORM)                   │
│  - Session Management  - Declarative Base  - Unit of Work / Transactions    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                              DATABASE STORAGE                               │
│         SQLite (Local Dev / Zero Config)  |  PostgreSQL (Production)        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Technology Stack & Directory Layout

### 2.1 Technology Selection
- **Runtime:** Python 3.11+ (Fast, modern typing, robust date handling).
- **Web Framework:** FastAPI (High-performance ASGI, automatic OpenAPI/Swagger documentation, native Pydantic schema validation).
- **ORM:** SQLAlchemy 2.0 (Explicit 2.0-style queries, strict type annotations, transaction demarcation).
- **Database Migrations:** Alembic (Versioned schema migrations with repeatable rollbacks).
- **Data Validation:** Pydantic v2 (Fast C-based schema validation and serialization).
- **Data Analysis & Export:** Pandas & OpenPyXL (Efficient CSV parsing, data normalization, and Excel report generation).
- **Testing:** Pytest & HTTPX (Unit tests, API integration tests, transaction rollback fixtures).

### 2.2 Backend Code Organization
```
backend/
├── app/
│   ├── main.py                  # FastAPI application entry point & middleware
│   ├── core/
│   │   ├── config.py            # Pydantic BaseSettings (env vars)
│   │   ├── security.py          # JWT creation/verification, password hashing
│   │   ├── permissions.py       # RBAC dependencies & role validators
│   │   └── logging.py           # Structured JSON logger configuration
│   ├── database/
│   │   ├── session.py           # Engine initialization & session factory
│   │   └── base.py              # DeclarativeBase with common mixins
│   ├── models/                  # SQLAlchemy 2.0 ORM entities
│   │   ├── user.py              # User, Role
│   │   ├── member.py            # MemberProfile
│   │   ├── source.py            # AcquisitionSource, SourceLink, AttributionEvent
│   │   ├── referral.py          # Referral, ReferralStage
│   │   ├── survey.py            # Survey, SurveyEligibilityRule, SurveyApplication
│   │   ├── participation.py     # SurveyParticipation
│   │   ├── import_job.py        # ImportJob, ImportRowError
│   │   ├── meta_lead.py         # MetaLead
│   │   ├── payout.py            # Payout
│   │   ├── fraud.py             # FraudFlag
│   │   └── audit.py             # AuditLog
│   ├── schemas/                 # Pydantic request/response models
│   │   ├── auth.py
│   │   ├── member.py
│   │   ├── source.py
│   │   ├── referral.py
│   │   ├── survey.py
│   │   ├── import_job.py
│   │   ├── meta_lead.py
│   │   └── payout.py
│   ├── api/
│   │   └── v1/
│   │       ├── router.py        # Master API v1 router
│   │       ├── auth.py          # OTP login, token refresh, logout
│   │       ├── members.py       # Member profile onboarding & updates
│   │       ├── sources.py       # Source CRUD, link generation, click tracking
│   │       ├── referrals.py     # Referral list (masked), stage update
│   │       ├── surveys.py       # Survey CRUD, rule config, live listings
│   │       ├── eligibility.py   # Eligibility calculation endpoint
│   │       ├── operations.py    # Ops queues: respondent review, payouts
│   │       ├── imports.py       # CSV upload, preview, commit, errors
│   │       ├── meta_leads.py    # Meta webhook / mock lead ingestion
│   │       └── analytics.py     # Admin KPI summaries & exports
│   ├── services/                # Encapsulated domain business logic
│   │   ├── auth_service.py
│   │   ├── attribution_service.py
│   │   ├── eligibility_engine.py
│   │   ├── referral_service.py
│   │   ├── survey_service.py
│   │   ├── import_pipeline.py
│   │   ├── meta_lead_service.py
│   │   ├── payout_service.py
│   │   └── fraud_service.py
│   ├── utils/                   # Phone normalization, date parsing, masking
│   └── tests/                   # Pytest test suite
│       ├── conftest.py
│       ├── test_auth.py
│       ├── test_eligibility.py
│       ├── test_referral.py
│       ├── test_import.py
│       └── test_meta_leads.py
├── alembic/                     # Database migration scripts
├── requirements.txt
└── .env.example
```

---

## 3. Frontend Technology Stack & User Experience

### 3.1 Technology Selection
- **Core Library:** React 18 with TypeScript (Strict type safety, modern functional components).
- **Build Tool:** Vite (Ultra-fast HMR, optimized production tree-shaking).
- **Styling & Design System:** Tailwind CSS with custom theme configuration inspired by modern enterprise SaaS (Deep Navy `#0F172A`, Royal Indigo `#4338CA`, Crisp White cards, Subtle Slate borders).
- **Component Primitives:** Radix UI / shadcn/ui patterns (Accessible dialogs, dropdowns, tooltips, tabs, sheets).
- **State & Server Cache:** TanStack Query v5 (React Query) for intelligent caching, auto-refetching, and zero stale UI data.
- **Form Management & Validation:** React Hook Form with Zod resolvers (Declarative client validation mirroring backend schemas).
- **Data Visualization:** Recharts (Responsive funnel charts, bar charts, and timeline line charts).
- **Routing:** React Router v6 (Nested layout routing, public/private route guards).
- **Icons:** Lucide React (Crisp, consistent stroke icons).

### 3.2 Dual Viewport Experience Design
1. **Respondent Portal (Mobile-First):**
   - Form-factor optimized for mobile screens ($360\text{px} - 430\text{px}$ width) with sticky bottom navigation, touch-friendly tap targets ($\ge 44\text{px}$), card-based survey feeds, and zero horizontal scrolling.
   - 1-tap OTP copy, prominent eligibility status pills, and simple referral share mechanics.
2. **Admin & Operations Portals (Desktop-First):**
   - Information-dense desktop layouts ($1280\text{px}+$ optimized) featuring collapsible sidebars, multi-metric KPI cards, interactive data grids with column sorting, debounced inline search, and multi-faceted filter drawers.

---

## 4. Security, Session & Data Integrity Architecture

### 4.1 Authentication & Session Management
- **Passwordless Mock OTP Flow:**
  1. Client sends `POST /api/v1/auth/otp/send` with Indian phone number (`9876543210`).
  2. Server generates a cryptographically secure 6-digit OTP stored in database with a 5-minute expiry.
  3. In development/demo mode, the OTP is returned in the API response and rendered in an on-screen toast or banner for effortless testing.
  4. Client submits `POST /api/v1/auth/otp/verify`.
  5. On verification, server issues:
     - `access_token` (JWT, signed with HMAC-SHA256, 15-minute lifespan) containing `sub` (User ID), `role` (Admin/Ops/Respondent), and `member_id`.
     - `refresh_token` (7-day lifespan).
- **Session Persistence:** Tokens stored securely in browser local storage or memory, attached via HTTP Authorization Bearer headers.

### 4.2 Role-Based Access Control (RBAC) Architecture
FastAPI dependencies act as gatekeepers on all routes:
```python
# app/core/permissions.py
def require_role(allowed_roles: list[RoleEnum]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient operational privileges")
        return current_user
    return role_checker
```

### 4.3 Data Privacy & Sensitive Information Masking
In accordance with consumer privacy best practices, respondents viewing their referrals must **never receive or view unmasked phone numbers**.
- **Transformation Layer:** All referral API responses execute backend masking:
  $$\text{Mask}(P) = P[:2] + \text{"XXXXXX"} + P[-2:] \quad \text{e.g., } 9876543210 \rightarrow 98\text{XXXXXX}10$$
  Full numbers are stripped before JSON serialization.

---

## 5. Domain Engines Specifications

### 5.1 Eligibility Engine Architecture
The eligibility engine evaluates whether a respondent is qualified for a survey project based on strict/flexible multi-attribute rules:

```
                          [ Respondent Profile + Survey Rules ]
                                            │
                                            ▼
                           [ Check 1: Survey Active & Deadline ]
                           └── Expired? ───────────────► REJECTED
                                            │
                                            ▼
                           [ Check 2: Quota Available ]
                           └── Quota Full? ────────────► REJECTED
                                            │
                                            ▼
                           [ Check 3: 3-Month Cool-off ]
                           └── Completed < 3 mos? ─────► REJECTED (with Next Date)
                                            │
                                            ▼
                           [ Check 4: Demographic Rules ]
                           ├── Age Range (min/max)
                           ├── Target Cities
                           ├── Target Genders
                           ├── Target Income Brackets
                           └── Matching Interests
                                            │
               ┌────────────────────────────┴───────────────────────────┐
               ▼                                                        ▼
       [ Any Strict Failed? ]                                  [ Any Flexible Failed? ]
               │                                                        │
               ├── YES ──────────────► REJECTED                         ├── YES ──► WAITLISTED
               └── NO                                                   └── NO  ──► APPROVED
```

### 5.2 Resilient CSV Import Architecture
The import pipeline operates through an isolated preview-and-commit pattern:
1. **Parser & Cleaner:** Streams rows, handles encoding (`utf-8`, `latin1`), ignores empty rows.
2. **Entity Normalizer:** Maps inconsistent strings to canonical values using dictionary lookups and regular expressions.
3. **Validator:** Checks mandatory columns (`name`, `phone`, `date_of_birth`, `gender`).
4. **Duplicate Inspector:** Compares against existing database records and intra-file rows.
5. **Preview Generator:** Returns structured breakdown: `{total, valid, duplicate, invalid, rows: [...]}`.
6. **Transactional Committer:** When confirmed by admin, commits valid records in a single database transaction.

### 5.3 Meta Ads Lead API Architecture
Simulates official Meta Leadgen Webhook and Graph API integration:
- Supports lead ingestion with campaign metadata (`leadgen_id`, `form_id`, `campaign_id`, `ad_id`, `field_data`).
- Enforces idempotency via unique constraints on `leadgen_id`.
- Automatically assigns acquisition source to dynamic record `Meta Ads`.
