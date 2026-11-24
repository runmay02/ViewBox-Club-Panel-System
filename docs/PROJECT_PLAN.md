# ViewBox Club — Comprehensive Project Plan & Execution Roadmap
**Concave Insights — Technical Assessment: Full Stack Developer (Python/React)**

---

## 1. Project Management Principles

The ViewBox Panel System development lifecycle strictly adheres to the Concave Insights 7-day assessment parameters. The execution methodology enforces:
1. **Incremental Architecture First:** Complete design and architectural contracts are documented and frozen before mass implementation.
2. **Day 2 Design Milestone Freeze:** The `/design` folder containing `user_flow.md`, `user_flow.png`, `database_schema.md`, `er_diagram.png`, and `architecture.md` is finalized and frozen on Day 2. Subsequent modifications are added as versioned artifacts without altering baseline contracts.
3. **Continuous Verification:** Every backend service is paired with automated Pytest unit and integration tests. No feature is marked "Complete" without live execution and verification.
4. **Git Discipline:** Clean, atomic commits corresponding to feature milestones with descriptive conventional commit messages.

---

## 2. Seven-Day Execution Roadmap & Daily Milestones

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                      VIEWBOX CLUB 7-DAY DELIVERY ROADMAP                      │
├───────┬──────────────────────────────────────┬────────────────────────────────┤
│ Day   │ Milestone & Focus                    │ Key Deliverables               │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 1 │ Architecture, Planning & Setup       │ Requirements, Arch, Schema,    │
│       │                                      │ Repository scaffold, Git init  │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 2 │ Design Milestone Freeze (Mandatory)  │ /design specifications,        │
│       │                                      │ ER diagram PNG, User flow PNG  │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 3 │ Core Backend & Identity              │ Mock OTP Auth, RBAC, Profile,  │
│       │                                      │ Dynamic Sources, Source Links  │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 4 │ Survey Engine & Respondent Portal    │ Eligibility Engine, Cool-off,  │
│       │                                      │ Quota locks, Mobile React UI   │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 5 │ Operations Workflow & Admin Panel    │ Data Grid, Filters, Exports,   │
│       │                                      │ Referral 3-Stage State Machine │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 6 │ Resilient Imports & Integrations     │ 11-Step CSV Pipeline, Meta API,│
│       │                                      │ Fraud Queue, Payout Ledger     │
├───────┼──────────────────────────────────────┼────────────────────────────────┤
│ Day 7 │ Stabilization, Testing & Submission  │ Automated Tests, README, Demo  │
│       │                                      │ Seeds, Video Walkthrough       │
└───────┴──────────────────────────────────────┴────────────────────────────────┘
```

### Day 1: Architecture, Requirements & Initial Scaffolding
- **Objectives:**
  - Ingest and deeply inspect `Concave_Insights_TechnicalAssessment_ViewBox_Panel_System.pdf` and `viewbox_respondents_sample.csv`.
  - Extract all functional and non-functional requirements, RBAC matrices, and dependency graphs.
  - Establish project repository, `.gitignore`, initial README, and folder structure.
- **Deliverables:**
  - `docs/REQUIREMENTS.md`
  - `docs/PROJECT_PLAN.md`
  - `docs/TECHNICAL_ARCHITECTURE.md`
  - Git repository initialization and baseline commits.

### Day 2: Design Submission Freeze (Mandatory Milestone)
- **Objectives:**
  - Create the complete normalized relational database schema (19 entities) with foreign keys, constraints, and indexes.
  - Create the detailed user journeys and state machine workflows across all three user roles.
  - Generate high-resolution visual PNG diagrams (`er_diagram.png` and `user_flow.png`).
  - Document system architecture, module boundaries, and deployment topology.
- **Deliverables:**
  - `design/database_schema.md`
  - `design/er_diagram.png`
  - `design/user_flow.md`
  - `design/user_flow.png`
  - `design/architecture.md`
  - Commit milestone: `chore: submit day 2 design milestone`.

### Day 3: Core Backend, Identity & Dynamic Sources
- **Objectives:**
  - Implement FastAPI backend application shell with CORS and error handling middleware.
  - Implement SQLAlchemy 2.0 models and initial Alembic database migrations.
  - Build mock OTP authentication service (`/auth/otp/send`, `/auth/otp/verify`) returning JWT tokens with role claims.
  - Implement Respondent Profile onboarding and management service.
  - Build Dynamic Acquisition Source CRUD and cryptographically secure tokenized link generator (`/sources`, `/sources/{id}/link`).
- **Verification:** Pytest test suite for OTP auth, JWT verification, and source link tokenization.

### Day 4: Survey Engine & Respondent Portal
- **Objectives:**
  - Implement Survey CRUD with strict 15-day lifecycle validation (`deadline <= start_date + 15 days`).
  - Implement multi-attribute Survey Eligibility Engine with Strict and Flexible rule evaluation.
  - Implement 3-month cool-off date arithmetic using calendar month math.
  - Implement survey quota locking with database transaction protection.
  - Build mobile-first React Respondent Portal:
    - Phone + Mock OTP login screen with on-screen debug helper.
    - First-time onboarding profile form with validation.
    - Respondent dashboard with interest matching, survey eligibility cards, and plain-language explanation modals.
    - "My Referrals" screen with phone number masking (`98XXXXXX21`).
- **Verification:** Unit tests for age limits, cool-off boundaries, quota exhaustion, and UI responsiveness.

### Day 5: Operations Workflow & Admin Management Panel
- **Objectives:**
  - Implement the Referral 3-Stage State Machine (`Lead` $\rightarrow$ `Fit` $\rightarrow$ `Completed` / `Failed`).
  - Implement Operations verification queues with mandatory failure reason recording.
  - Build Admin Panel desktop experience:
    - Executive KPI dashboard cards and Recharts analytics (signup trend, source breakdown, referral funnel).
    - High-density respondent data grid with debounced search (`name`, `id`, `city`, `phone`).
    - Multi-column filtering by city, source, and operational status.
    - Contextual CSV and Excel (`.xlsx`) export of the filtered grid view.
- **Verification:** End-to-end referral transition testing and export file format verification.

### Day 6: Resilient CSV Import Pipeline & Meta Ads API
- **Objectives:**
  - Build the 11-step resilient CSV import pipeline capable of ingesting `viewbox_respondents_sample.csv`:
    - Header inspection, encoding detection, and empty-row skipping.
    - Normalization of gender, cities, acquisition sources, income ranges, and varied date formats.
    - Duplicate detection (member ID and phone number).
    - Two-phase import: Interactive web preview with error categorization, followed by atomic transaction commit.
  - Implement Meta Ads mock webhook endpoint (`POST /api/v1/integrations/meta/leads`) with idempotency and campaign metadata storage.
  - Implement Bonus Modules:
    - Fraud & duplicate review quarantine queue.
    - Payout ledger with calculation and two-step approval.
- **Verification:** Ingestion test against messy sample CSV; Meta API payload tests with duplicate lead handling.

### Day 7: Hardening, Automated Testing, Documentation & Submission
- **Objectives:**
  - Run comprehensive end-to-end integration tests covering full business journeys.
  - Polish UI/UX states across all portals: loading spinners, empty states, error toasts, and mobile layouts.
  - Finalize `README.md` following the exact 9-section assessment template with demo credentials and API documentation.
  - Create demo data seed script (`scripts/seed_demo_data.py`).
  - Record 3-5 minute demonstration video.
- **Deliverables:**
  - Complete `README.md`.
  - Passing test suite (`pytest` and frontend tests).
  - Clean Git commit history.

---

## 3. Technical Risk Analysis & Mitigation Matrix

| Risk Event | Severity | Probability | Impact | Mitigation Strategy |
|:---|:---:|:---:|:---|:---|
| **Messy CSV Parser Crash** | Critical | High | Entire import pipeline halts on malformed rows | Implement row-level exception isolation; malformed rows are quarantined to error log while valid rows continue. |
| **Date Format Ambiguity (e.g. 02-05-26)** | High | High | Wrong DOB or survey completion date stored | Multi-pass regex parser checking ISO, DD/MM/YYYY, and DD-MM-YY with Indian market context precedence (DD/MM). |
| **Survey Quota Race Condition** | High | Medium | Quota exceeded under concurrent applicants | Enforce atomic updates with `WHERE completed_count < target_quota` in serializable database transactions. |
| **Cool-Off Calculation Errors** | Medium | Medium | Ineligible members approved for surveys | Use Python `relativedelta(months=+3)` to strictly honor calendar month additions and leap years. |
| **SQLite Concurrency Contention** | Medium | Low | Database locked errors during parallel operations | Set SQLite WAL mode (`PRAGMA journal_mode=WAL;`) with 10s busy timeout in SQLAlchemy engine configuration. |
| **Accidental Phone Number Leakage** | Critical | Low | Data privacy violation for referred users | Mandatory DTO/schema level phone masking (`98XXXXXX21`) before returning referral JSON. |

---

## 4. Quality Assurance & Testing Strategy

### 4.1 Backend Test Coverage
- **Authentication:** Valid OTP, expired OTP, invalid OTP, token refresh, role authorization checks.
- **Attribution & Sources:** Tokenized link resolution, fallback dropdown, attribution cookie preservation.
- **Eligibility Engine:**
  - Age: within range, below minimum, above maximum.
  - City & Gender: exact match, flexible mismatch, strict mismatch.
  - Cool-off: 1 day before 3 months (rejected), exactly 3 months (approved).
  - Quota: 1 slot remaining (approved), 0 slots (rejected).
  - Deadline: active survey, survey expired by 1 minute.
- **Referral Workflow:** Self-referral rejection, duplicate referral prevention, valid transition (`Lead` $\rightarrow$ `Fit` $\rightarrow$ `Completed`), rejection on invalid transitions.
- **CSV Ingestion:** Clean rows, malformed dates, truncated phones, duplicate member IDs, empty lines, partial import.
- **Meta Ads API:** Valid payload, duplicate lead ID, missing mandatory phone, invalid phone format.

### 4.2 End-to-End Business Journey Verification
Automated integration test executing the complete Concave Insights lifecycle:
1. Admin creates source "WhatsApp Group - Mumbai" $\rightarrow$ generates link `/join?source_token=xyz`.
2. Respondent A visits link $\rightarrow$ signs up via mock OTP $\rightarrow$ completes profile $\rightarrow$ assigned source.
3. Respondent A copies personal referral link $\rightarrow$ Respondent B visits referral link.
4. Respondent B signs up $\rightarrow$ Referral record created (`Stage: Lead`).
5. Operations reviews Respondent B $\rightarrow$ marks `Stage: Fit`.
6. Respondent B applies for Survey X $\rightarrow$ Eligibility engine confirms `APPROVED`.
7. Respondent B completes Survey X.
8. Operations verifies Survey completion $\rightarrow$ marks Referral `Stage: Completed`.
9. Respondent A views dashboard $\rightarrow$ sees Respondent B as `Completed` with bonus earned.
10. Payout ledger logs ₹250 survey incentive for B and ₹100 referral bonus for A $\rightarrow$ Operations approves.
