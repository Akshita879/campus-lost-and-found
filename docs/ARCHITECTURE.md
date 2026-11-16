# System Architecture & Design — Campus Lost & Found Portal

## 1. Architectural Style
The Campus Lost & Found Portal is engineered as a **Clean Modular Monolith**:
- Business logic is completely decoupled from HTTP transport and routing.
- All core domains (Auth, Reports, Matching, Claims) are isolated into dedicated service classes.
- APIs adhere to REST conventions with strict Pydantic v2 validation contracts.
- Database access uses SQLAlchemy 2.0 ORM conventions with transactions managed per request.
- The frontend is completely decoupled as a client communicating via standard HTTP/JSON REST APIs with configurable CORS.

```
┌────────────────────────────────────────────────────────────────┐
│                   Frontend Presentation Layer                  │
│       (Current: Temporary Vanilla JS / Target: React+Tailwind) │
└───────────────────────────────┬────────────────────────────────┘
                                │ HTTP / REST JSON
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                    FastAPI Gateway & Routers                   │
│           (/api/v1/auth, /api/v1/reports, /api/v1/claims)      │
└───────────────────────────────┬────────────────────────────────┘
                                │ Dependency Injection
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                     Service & Business Layer                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐ │
│  │ AuthService  │ │ReportService │ │MatchingEngine│ │ Claim  │ │
│  │ (Argon2+JWT) │ │ (CRUD+Upload)│ │  (RapidFuzz) │ │Service │ │
│  └──────────────┘ └──────────────┘ └──────────────┘ └────────┘ │
└───────────────────────────────┬────────────────────────────────┘
                                │ ORM Sessions
                                ▼
┌────────────────────────────────────────────────────────────────┐
│               Data Access Layer (SQLAlchemy 2.0)               │
│               Models: User, Report, Claim                      │
└───────────────────────────────┬────────────────────────────────┘
                                │ PyMySQL Driver
                                ▼
┌────────────────────────────────────────────────────────────────┐
│                    Database Storage Layer                      │
│                    MySQL 8.0 Engine                            │
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### A. Authentication Module (`app/services/auth_service.py`)
- Password hashing is powered by **Argon2id** (`argon2-cffi`), the winner of the Password Hashing Competition. Plaintext passwords are never persisted.
- Authentication tokens are standard signed **JWTs** (HMAC-SHA256) containing subject claims and expiration timestamps.
- Token validation is handled via FastAPI's `OAuth2PasswordBearer` dependency with centralized user resolution.

### B. Report Management Module (`app/services/report_service.py`)
- Manages single unified table for both `LOST` and `FOUND` property.
- Enforces strict ownership rules: only the creating user can update or close their report.
- Deletion is performed via **soft-closure** (`status = CLOSED`), ensuring audit trails and historical records remain intact.
- Search and filtering uses database-level query construction (`ilike`, range filters, pagination offset/limit) to ensure minimal memory overhead.
- Public report endpoints do not expose personal emails, password hashes, or private verification details.

### C. File Upload Security (`app/utils/image_handler.py`)
- Validates MIME type (`image/jpeg`, `image/png`, `image/webp`) and file extensions.
- Enforces a 5MB maximum file size limit.
- Generates server-side UUID filenames to prevent path traversal and overwrite vulnerabilities.
- Relative paths are recorded in MySQL while files are stored locally under `backend/uploads/`.

### D. Deterministic Matching Engine (`app/services/matching_service.py`)
- **Zero External AI/Cloud Dependencies:** Operates 100% deterministically using localized fuzzy string comparison.
- **Rules:**
  1. Compares a `LOST` report exclusively against `ACTIVE` `FOUND` candidates.
  2. Excludes reports with status `CLOSED` or `RESOLVED`.
  3. Never matches lost items against other lost items.
- **Scoring Breakdown:**
  $$\text{Total Score} = 0.30 \times \text{Cat} + 0.30 \times \text{Name} + 0.20 \times \text{Desc} + 0.10 \times \text{Loc} + 0.10 \times \text{Date}$$
  - **Category (30%):** Exact match = 100%, different = 0%.
  - **Item Name (30%):** RapidFuzz `token_set_ratio` normalized to 0–100%.
  - **Description (20%):** RapidFuzz `token_set_ratio` normalized to 0–100%.
  - **Location (10%):** RapidFuzz `token_set_ratio` on campus location name.
  - **Date Proximity (10%):** Calendar decay function (100% same day, 10% penalty per day up to 7 days, gradual decay up to 14 days, 0% thereafter).
- Explains the match score via a detailed attribute breakdown so users understand why candidate items surfaced.
- **Important:** Matching scores express textual similarity, never automatic declaration of ownership.

### E. Claim Management Module (`app/services/claim_service.py`)
- Enforces strict business validations:
  - Claims can only be filed against `ACTIVE` `FOUND` items.
  - A user cannot claim their own found item.
  - An optional linked `LOST` report must belong to the claimant and be of type `LOST`.
  - Prevents duplicate active `PENDING` claims by the same claimant for the same found item.
- **Privacy Assurance:** `verification_details` are strictly private and cannot be viewed by other users or the finder.
- **Workflow State:** Claims remain `PENDING` until physical verification by campus authorities. No automatic claim approval or premature item resolution is permitted.
- Claimant may safely withdraw their pending claim (`status = WITHDRAWN`).
