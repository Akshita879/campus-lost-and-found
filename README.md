# Campus Lost & Found Portal

**Problem Statement:** PS-03 — Campus Lost and Found Portal  
**Category:** Web Development  
**Hackathon:** FMH CodeSprint Mini Hackathon 2026  

---

## 👥 Team Details

- **Participant 1:** Akshita A
- **Participant 2:** Sourabh
- **Participant 2:** Sneha A

---

## 🚀 Live Deployment

This project is deployed on **Vercel** (React + FastAPI multi-service) with a **FreeDB** MySQL database.

**Live app:** [https://campus-lost-and-found-six-pied.vercel.app/](https://campus-lost-and-found-six-pied.vercel.app/)

### Admin credentials

| Field | Value |
|--------|--------|
| Admin email | `admin@campus.edu` |
| Admin password | `AdminPass123` |

Admin login page: [https://campus-lost-and-found-six-pied.vercel.app/admin/login](https://campus-lost-and-found-six-pied.vercel.app/admin/login)

---

## 📌 Problem

Students and staff frequently lose personal belongings around campus—including student ID cards, keys, textbooks, water bottles, calculators, wallets, and electronic accessories. Without a centralized reporting and matching mechanism:
- Finding lost property relies on scattered physical notice boards, chaotic messaging groups, or word-of-mouth.
- Recovering property takes days or fails entirely.
- Publicly displaying sensitive student information (such as ID cards or phone numbers) poses safety and privacy risks.
- Handing over found items without a safe ownership verification workflow leads to false claims or theft.

---

## 💡 Proposed Solution

We developed a centralized, secure, privacy-first web application where students and staff can:
1. Submit structured reports for both **LOST** and **FOUND** items.
2. Search and filter active items by keyword, category, campus location, and date range.
3. Automatically discover candidate matches using a **deterministic, explainable matching engine** (powered by RapidFuzz) that scores textual and contextual similarity without external AI costs or latency.
4. Safely claim found items by submitting private verification details that are hidden from the public and the finder, reserved for physical verification by campus authorities.

---

## ✨ Key Features

### ✅ Implemented & Working Features (MVP)
- **User Authentication:** Registration and login secured with **Argon2id** password hashing and **JWT** (JSON Web Token) bearer tokens.
- **Unified Reports:** Create, view, update, and soft-delete (`status = CLOSED`) both `LOST` and `FOUND` listings.
- **Secure File Uploads:** Upload item photos (JPEG, PNG, WEBP, max 5MB) with UUID-based server-side naming and path traversal protection.
- **Database-Level Search & Filtering:** Dynamic query filtering across item names, descriptions, categories, campus locations, and date ranges with pagination.
- **Deterministic Matching Engine:** Evaluates `LOST` reports against active `FOUND` items across 5 weighted attributes:
  - Category Match: 30%
  - Item Name Similarity: 30%
  - Description Similarity: 20%
  - Campus Location Similarity: 10%
  - Date Proximity Decay: 10%
  - *Transparent Score Breakdown:* Provides visual feedback on how similarity was calculated.
- **Safe Claim Workflow:** Submit claims against found items with private verification details. Prevents users from claiming their own found items or submitting duplicate claims.
- **Claim Tracking & Withdrawal:** Claimants can view their submitted claims and withdraw pending claims.
- **Privacy Protections:** Student emails, password hashes, and claim verification details are strictly excluded from public APIs.
- **Responsive Temporary Frontend:** Fully operational HTML5, CSS3, and Vanilla JavaScript single-page application connected to live REST endpoints.

### ⏳ Planned / Future Enhancements (Post-Hackathon)
- Campus administrator / moderator approval portal for physical handover verification.
- Push notifications / email alerts when a high-probability match is detected.
- Geolocation map picker for campus landmarks.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Decoupled Single Page Application)
- **Backend:** Python 3.11+, FastAPI (REST API with OpenAPI / Swagger)
- **Database:** MySQL 8.0 with PyMySQL driver
- **ORM & Migrations:** SQLAlchemy 2.0 & Alembic
- **Data Validation:** Pydantic v2 & Pydantic Settings
- **Authentication & Cryptography:** Argon2id (`argon2-cffi`) & PyJWT (`HS256`)
- **Matching Engine:** RapidFuzz (fuzzy string comparison, token set ratio)
- **Testing:** Pytest (35 automated unit/integration tests) & HTTPX / TestClient

---

## 🏗️ Application Workflow & Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Frontend Client                      │
│        (HTML5 / CSS3 / Vanilla JS SPA at /ui/)         │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / REST JSON
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Application                    │
│   ├── /api/v1/auth    (Register, Login, /me)           │
│   ├── /api/v1/reports (CRUD, Uploads, Search, Matches) │
│   └── /api/v1/claims  (Submit, Track, Withdraw)        │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐ ┌───────────────────────┐
│     Services & Business      │ │   Matching Engine     │
│   - AuthService (Argon2+JWT) │ │   - RapidFuzz Score   │
│   - ReportService (Queries)  │ │   - 5-Attribute Decay │
│   - ClaimService (Privacy)   │ │   - Explainable Meter │
└──────────────┬───────────────┘ └───────────────────────┘
               │
               ▼
┌──────────────────────────────┐
│  SQLAlchemy 2.0 / Alembic    │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       MySQL 8.0 Database     │
│  (users, reports, claims)    │
└──────────────────────────────┘
```

---

## 🚀 Installation and Setup

### 1. Prerequisites
- Python 3.11+
- MySQL Server 8.0+ running on port `3306`

### 2. Database Configuration
Ensure MySQL has the database created:
```sql
CREATE DATABASE IF NOT EXISTS campus_lost_and_found CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Configure your local connection in `backend/.env` (use `.env.example` as a template):
```ini
DATABASE_URL="mysql+pymysql://root:your_password@127.0.0.1:3306/campus_lost_and_found"
JWT_SECRET_KEY="your_secure_random_jwt_secret"
```
*(Never commit `.env` with actual production secrets).*

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run Database Migrations
Apply Alembic migrations to set up all tables and indexes:
```bash
cd backend
alembic upgrade head
```

### 5. Start the Application
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📖 How to Use

1. **Access the Portal:** Open your browser to `http://localhost:8000/ui/`.
2. **Register & Login:** Click **Login / Register** in the top navigation to create an account.
3. **Report Lost / Found:**
   - Click **Report Item**.
   - Toggle between **LOST** and **FOUND**.
   - Fill in the item name, category, approximate date, campus location, description, and optional photo.
4. **Browse & Search:**
   - Filter active reports by keyword, category, date, or campus location.
5. **View Algorithmic Matches:**
   - On any of your `LOST` reports (under **My Reports**), click **🎯 View Matches**.
   - The matching engine ranks candidates and provides a percentage breakdown.
6. **Submit a Claim:**
   - Click **🛡️ Claim This Item** on a matching found item.
   - Enter private verification details (e.g., unique scratch, sticker, or serial markings).
7. **Track or Withdraw Claims:**
   - View your pending claims under **My Claims**.
   - Withdraw a claim anytime with the **Withdraw Claim** button.

---

## 🧪 Testing

### 1. Automated Pytest Suite (35 Tests)
Runs against an isolated in-memory test database validating Authentication, Reports, Search, Matching, and Claim Privacy:
```bash
cd backend
pytest -v
```
**Results:** `35 passed in 3.16s` (100% pass rate).

### 2. 14-Step End-to-End Acceptance Test
Validates the complete hackathon test journey against MySQL:
```bash
python verify_acceptance.py
```
**Acceptance Scenarios Verified:**
- Student 1 (Alice) registers and logs in.
- Alice reports a LOST blue water bottle at Central Library.
- Student 2 (Bob) registers, logs in, and reports a FOUND matching bottle.
- Alice browses reports and queries the matching engine.
- Matching engine surfaces Bob's item with a **94.6% similarity score**.
- Alice files a claim with private verification details (`status: PENDING`).
- Bob is blocked (`403 Forbidden`) from viewing Alice's private claim details.
- Alice withdraws her claim; item remains uncompromised.

---

## 🤖 AI, APIs, and Third-Party Resources Disclosure

As required by the FMH CodeSprint guidelines:
- **Frameworks & Libraries:** FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PyMySQL, RapidFuzz, argon2-cffi, PyJWT, pytest.
- **Deterministic Matching:** Implemented directly in Python using **RapidFuzz** (token set ratio) with custom decay mathematics. **No third-party AI APIs, cloud LLMs, or paid external services** were used for matching, ensuring zero latency, zero cost, and predictable explainability.
- **AI Coding Assistance:** Antigravity (Google DeepMind) was used as an AI development assistant to plan architecture, scaffold boilerplate code, assist with Alembic migrations, and author automated test fixtures. All business rules, matching weights, security validations, and endpoints were verified and tested locally.

---

## ⚠️ Known Limitations

1. **Moderator Handover Workflow:** In this MVP, claims remain `PENDING` to prevent fraudulent auto-approvals. An administrative dashboard for campus staff to physically mark claims `RESOLVED` is designed for Phase 2.
2. **Text-Based Campus Locations:** Location matching relies on campus place names (e.g. "Central Library", "Science Block"). GPS coordinates or floorplan mapping are not included in this version.

---

## 🔮 Future Improvements

1. **Role-Based Moderator Portal:** Dedicated admin dashboard for campus security / student council to review claims and verify student ID before handover.
2. **Automated Notification Alerts:** Email or SMS notifications when an item scoring above 80% similarity is reported.
3. **Interactive Campus Map:** Leaflet / OpenStreetMap integration for visual lost/found pin drops.
4. **React / Tailwind Production Frontend:** Full replacement of the temporary demonstration UI with a production React.js/Vite frontend.

---

## 🔗 Demo & Repository Links

- **Local Web Application:** `http://localhost:8000/ui/`
- **Interactive API Swagger Docs:** `http://localhost:8000/docs`
- **ReDoc Documentation:** `http://localhost:8000/redoc`
- **Source Code Repository:** [Add your GitHub repository URL here]
