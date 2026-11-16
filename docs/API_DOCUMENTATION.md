# API Documentation — Campus Lost & Found Portal

Base URL: `http://localhost:8000/api/v1`  
Interactive Swagger UI: `http://localhost:8000/docs`  
ReDoc: `http://localhost:8000/redoc`

---

## 1. Authentication Endpoints

### Register User
- **Method & Path:** `POST /auth/register`
- **Access:** Public
- **Request Body:**
  ```json
  {
    "name": "Alice Green",
    "email": "alice@campus.edu",
    "password": "SecurePassword123"
  }
  ```
- **Responses:**
  - `201 Created`:
    ```json
    {
      "id": 1,
      "name": "Alice Green",
      "email": "alice@campus.edu",
      "created_at": "2026-11-15T13:52:10.851852"
    }
    ```
  - `409 Conflict`: Email already registered
  - `422 Unprocessable Entity`: Validation error (e.g., password < 8 characters)

### User Login
- **Method & Path:** `POST /auth/login`
- **Access:** Public
- **Request Body:** JSON or `application/x-www-form-urlencoded`
  ```json
  {
    "email": "alice@campus.edu",
    "password": "SecurePassword123"
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer",
      "user": {
        "id": 1,
        "name": "Alice Green",
        "email": "alice@campus.edu",
        "created_at": "2026-11-15T13:52:10.851852"
      }
    }
    ```
  - `401 Unauthorized`: Invalid credentials

### Current User Profile
- **Method & Path:** `GET /auth/me`
- **Access:** Authenticated (`Authorization: Bearer <token>`)
- **Responses:**
  - `200 OK`: User profile object
  - `401 Unauthorized`: Token missing or expired

---

## 2. Report Management Endpoints

### Create Report (JSON)
- **Method & Path:** `POST /reports`
- **Access:** Authenticated
- **Request Body:**
  ```json
  {
    "item_name": "Blue Water Bottle",
    "category": "Bottle",
    "description": "Milton 750ml blue metallic water bottle with black cap",
    "report_type": "LOST",
    "approximate_date": "2026-11-15",
    "location": "Central Library"
  }
  ```
- **Responses:**
  - `201 Created`: Public report object (status: `ACTIVE`)
  - `401 Unauthorized`: Not authenticated

### Create Report with Image (Multipart Form)
- **Method & Path:** `POST /reports/upload`
- **Access:** Authenticated
- **Form Fields:** `item_name`, `category`, `description`, `report_type`, `approximate_date`, `location`
- **File Field:** `image` (JPEG, PNG, WEBP, max 5MB)
- **Responses:**
  - `201 Created`: Public report object with relative `image_path`
  - `400 Bad Request`: Invalid image extension or file exceeds size limit

### Browse Active Reports
- **Method & Path:** `GET /reports`
- **Access:** Public
- **Query Parameters:**
  - `page` (default 1)
  - `page_size` (default 10)
  - `report_type` (Optional: `LOST` or `FOUND`)
- **Responses:**
  - `200 OK`: Paginated list of active reports (`items`, `total`, `page`, `page_size`, `total_pages`)

### Search & Filter Reports
- **Method & Path:** `GET /reports/search`
- **Access:** Public
- **Query Parameters:**
  - `keyword` (matches `item_name` or `description`)
  - `category` (fuzzy matches `category`)
  - `report_type` (`LOST` or `FOUND`)
  - `location` (campus location filter)
  - `date_from` (ISO date YYYY-MM-DD)
  - `date_to` (ISO date YYYY-MM-DD)
  - `status` (Optional: defaults to `ACTIVE` and `CLAIM_PENDING`, excludes `CLOSED`/`RESOLVED`)
  - `page` (int)
  - `page_size` (int)
- **Responses:**
  - `200 OK`: Paginated results

### Get My Reports
- **Method & Path:** `GET /reports/my`
- **Access:** Authenticated
- **Responses:**
  - `200 OK`: List of all reports submitted by the authenticated user

### Get Report Details
- **Method & Path:** `GET /reports/{report_id}`
- **Access:** Public
- **Responses:**
  - `200 OK`: Report details (does NOT expose personal email or password)
  - `404 Not Found`: Report ID does not exist

### Update Report
- **Method & Path:** `PUT /reports/{report_id}`
- **Access:** Authenticated (Report Owner Only)
- **Request Body:** Partial fields (`item_name`, `category`, `description`, `location`, `status`)
- **Responses:**
  - `200 OK`: Updated report object
  - `403 Forbidden`: User does not own the report
  - `404 Not Found`: Report not found

### Close Report (Soft Delete)
- **Method & Path:** `DELETE /reports/{report_id}`
- **Access:** Authenticated (Report Owner Only)
- **Responses:**
  - `200 OK`: Report with status updated to `CLOSED`
  - `403 Forbidden`: Not owner

---

## 3. Potential Matching Engine Endpoints

### Get Potential Matches for Lost Report
- **Method & Path:** `GET /reports/{report_id}/matches`
- **Access:** Authenticated
- **Business Logic:**
  - Target report must exist, be of type `LOST`, and be `ACTIVE`.
  - Compares against all `ACTIVE` `FOUND` items.
  - Computes weighted score across 5 attributes:
    1. Category similarity (weight 30)
    2. Item name similarity (weight 30)
    3. Description similarity (weight 20)
    4. Location similarity (weight 10)
    5. Date proximity decay (weight 10)
  - Ranks descending and filters below threshold (default 25%).
- **Responses:**
  - `200 OK`:
    ```json
    {
      "lost_report_id": 1,
      "lost_item_name": "Blue Water Bottle",
      "matches": [
        {
          "found_report_id": 2,
          "item_name": "Blue Milton Water Bottle",
          "category": "Bottle",
          "description": "Found a blue metallic Milton water bottle on study table",
          "location": "Central Library",
          "approximate_date": "2026-11-15",
          "image_path": null,
          "similarity_score": 94.6,
          "match_status": "POTENTIAL_MATCH",
          "score_breakdown": {
            "category": 100.0,
            "item_name": 100.0,
            "description": 73.1,
            "location": 100.0,
            "date": 100.0
          }
        }
      ]
    }
    ```
  - `400 Bad Request`: If called on a FOUND report
  - `404 Not Found`: If report ID does not exist

---

## 4. Claim Management Endpoints

### Submit Claim
- **Method & Path:** `POST /claims`
- **Access:** Authenticated
- **Request Body:**
  ```json
  {
    "report_id": 2,
    "lost_report_id": 1,
    "verification_details": "Under the bottom base there is a yellow barcode sticker."
  }
  ```
- **Business Rules:**
  - `report_id` must reference an `ACTIVE` `FOUND` report.
  - User cannot claim their own found report.
  - `lost_report_id` is optional; if provided, must belong to claimant and be `LOST`.
  - Prevent duplicate active (`PENDING`) claims for same found item.
  - Does NOT automatically resolve or handover the item.
- **Responses:**
  - `201 Created`: Claim object (status: `PENDING`)
  - `400 Bad Request`: Invalid report type or claiming own item
  - `403 Forbidden`: Linked lost report does not belong to claimant
  - `409 Conflict`: Duplicate pending claim exists

### Get My Claims
- **Method & Path:** `GET /claims/my`
- **Access:** Authenticated
- **Responses:**
  - `200 OK`: List of all claims filed by the authenticated user

### Get Claim Details
- **Method & Path:** `GET /claims/{claim_id}`
- **Access:** Authenticated (Claimant Only)
- **Responses:**
  - `200 OK`: Complete claim details including private verification information
  - `403 Forbidden`: Another user attempted to view private claim details
  - `404 Not Found`: Claim not found

### Withdraw Claim
- **Method & Path:** `POST /claims/{claim_id}/withdraw`
- **Access:** Authenticated (Claimant Only)
- **Responses:**
  - `200 OK`: Updated claim object with status `WITHDRAWN`
  - `400 Bad Request`: Claim is not in `PENDING` status
  - `403 Forbidden`: Not claimant
