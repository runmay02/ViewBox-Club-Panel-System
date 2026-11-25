# ViewBox Club Panel System

React/Vite frontend and FastAPI/SQLAlchemy API for respondent, survey and referral operations. The current working tree includes API integrations and workflow changes that are not represented in the committed Git history yet.

## Run locally

Requirements: Python 3.10+ and Node.js/npm. From the repository root:

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API creates missing tables and seeds the baseline acquisition sources plus admin/operations users on startup. It uses `backend/viewbox.db` by default. There are no Alembic migration scripts or `scripts/seed_demo_data.py` in this checkout; schema changes currently rely on SQLAlchemy `create_all`, which does not migrate existing databases.

In another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL` if the API is not at `http://127.0.0.1:8000`. Set backend values through `backend/.env`; see `backend/.env.example`. Configure `CORS_ORIGINS` for the deployed frontend. In development, mock OTP is returned by `/auth/otp/send`.

Demo internal accounts: `9999900001` (ADMIN) and `9999900002` (OPERATIONS), OTP `123456`. Any valid 10-digit phone can create a respondent account. There is no pre-seeded respondent profile.

## Verification

```powershell
cd backend
venv\Scripts\python.exe -m pytest -q
cd ..\frontend
npm run lint
npm run build
```

The backend tests use isolated temporary SQLite databases and exercise source/referral attribution, strict/flexible rules, cool-off, deadlines, role guards, messy CSV, export, and Meta duplicate handling. They do not replace deployment database migration checks or full browser QA.

## Implemented workflow surface

- OTP authentication, JWT access/refresh, role guards, respondent onboarding and profile edits.
- Source registry, tokenized link tracking, source attribution on onboarding and source analytics.
- Survey creation with strict/flexible rules, respondent feed, application status, deadlines, cool-off, quota enforcement and operations completion verification.
- Referral tracking with masked respondent-facing phone, operations stage changes and pending bonus ledger entry after FIT plus verified survey completion.
- Respondent administration grid with filtered CSV/XLSX exports, KPI/source analytics, CSV upload normalization and downloadable row errors.
- Meta lead webhook with optional shared secret, lead ID idempotency and duplicate phone flags.

## Known limitations

- CSV upload currently imports rows immediately; it does not provide the assessment's preview-then-confirm transaction flow. Historical fields and `referred_by` from the sample are not fully imported.
- Survey UI supports creation/rules and progress listing; editing surveys, configuring quotas by city/gender, and applicant log/progress management remain incomplete.
- Operations respondent triage and a dedicated fraud review queue are incomplete. Referral and payout queues exist.
- Meta integration is a mock webhook contract, not verified against Meta's live signature protocol. Rate limiting, SMS delivery and payout provider dispatch are not implemented.
- Mobile layout has responsive CSS breakpoints but has not had verified browser/device QA in this workspace.
- No migration history is present. Do not apply model changes to an existing production DB without a migration plan and backup.

## Project references

- [Requirements](docs/REQUIREMENTS.md)
- [Architecture](design/architecture.md)
- [Database schema](design/database_schema.md)
- [Respondent sample CSV](reference/viewbox_respondents_sample.csv)
