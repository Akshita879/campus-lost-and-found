# Database Schema Documentation — Campus Lost & Found Portal

Database Engine: **MySQL 8.0**  
ORM: **SQLAlchemy 2.0**  
Migration Tool: **Alembic**  
Default Collation: `utf8mb4_unicode_ci`

---

## Entity Relationship Overview

```
 ┌───────────────┐
 │     users     │
 └───────┬───────┘
         │ 1:N
         ├────────────────────────────────────────┐
         │                                        │
         ▼                                        ▼
 ┌───────────────┐        1:N (claims)    ┌───────────────┐
 │    reports    │◄───────────────────────┤    claims     │
 └───────────────┘                        └───────────────┘
         ▲                                        │
         │ (optional 1:1 linked lost report)       │
         └────────────────────────────────────────┘
```

---

## 1. Table: `users`
Stores student and staff credentials and account metadata.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique identifier for user |
| `name` | `VARCHAR(100)` | `NOT NULL` | Full name of the student or staff member |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE`, `INDEX` | Campus email address |
| `password_hash` | `VARCHAR(255)` | `NOT NULL` | Argon2id secure password hash |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Account creation timestamp |
| `updated_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Last profile update timestamp |

### Indexes
- `PRIMARY (id)`
- `ix_users_email (email)` UNIQUE

---

## 2. Table: `reports`
Stores both `LOST` and `FOUND` item reports in a unified structure.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique report identifier |
| `user_id` | `INT` | `NOT NULL`, `INDEX`, `FK -> users(id) ON DELETE CASCADE` | Creator of report |
| `item_name` | `VARCHAR(255)` | `NOT NULL`, `INDEX` | Title / name of item |
| `category` | `VARCHAR(100)` | `NOT NULL`, `INDEX` | Category (e.g., Bottle, Electronics, Books) |
| `description` | `TEXT` | `NOT NULL` | Detailed item description |
| `report_type` | `VARCHAR(20)` | `NOT NULL`, `INDEX` | `LOST` or `FOUND` |
| `approximate_date` | `DATE` | `NOT NULL`, `INDEX` | Date the item was lost or found |
| `location` | `VARCHAR(255)` | `NOT NULL`, `INDEX` | Campus location |
| `image_path` | `VARCHAR(500)` | `NULLABLE` | Relative path to uploaded image file |
| `status` | `VARCHAR(20)` | `NOT NULL`, `INDEX`, `DEFAULT 'ACTIVE'` | `ACTIVE`, `CLAIM_PENDING`, `RESOLVED`, `CLOSED` |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Creation timestamp |
| `updated_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Update timestamp |

### Indexes
- `PRIMARY (id)`
- `ix_reports_user_id (user_id)`
- `ix_reports_item_name (item_name)`
- `ix_reports_category (category)`
- `ix_reports_report_type (report_type)`
- `ix_reports_approximate_date (approximate_date)`
- `ix_reports_location (location)`
- `ix_reports_status (status)`

---

## 3. Table: `claims`
Stores ownership claims filed against found reports.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INT` | `PRIMARY KEY`, `AUTO_INCREMENT` | Unique claim identifier |
| `report_id` | `INT` | `NOT NULL`, `INDEX`, `FK -> reports(id) ON DELETE CASCADE` | The target `FOUND` report |
| `claimant_id` | `INT` | `NOT NULL`, `INDEX`, `FK -> users(id) ON DELETE CASCADE` | The user filing the claim |
| `lost_report_id` | `INT` | `NULLABLE`, `INDEX`, `FK -> reports(id) ON DELETE SET NULL` | Optional linked `LOST` report |
| `verification_details` | `TEXT` | `NOT NULL` | Private identifying details |
| `status` | `VARCHAR(20)` | `NOT NULL`, `INDEX`, `DEFAULT 'PENDING'` | `PENDING`, `WITHDRAWN` |
| `created_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Submission timestamp |
| `updated_at` | `DATETIME` | `NOT NULL`, `DEFAULT UTC_TIMESTAMP` | Last status update timestamp |

### Indexes
- `PRIMARY (id)`
- `ix_claims_report_id (report_id)`
- `ix_claims_claimant_id (claimant_id)`
- `ix_claims_lost_report_id (lost_report_id)`
- `ix_claims_status (status)`

---

## 4. Table: `alembic_version`
Managed by Alembic migration tracking.

| Column | Type | Constraints |
|---|---|---|
| `version_num` | `VARCHAR(32)` | `PRIMARY KEY` |
