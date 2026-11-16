from fastapi import status


def test_claim_submission_success(client, auth_headers_user1, auth_headers_user2):
    # 1. User 1 creates LOST report
    lost = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Blue Water Bottle",
            "category": "Bottle",
            "description": "Lost near library",
            "report_type": "LOST",
            "approximate_date": "2026-11-12",
            "location": "Library"
        },
        headers=auth_headers_user1
    ).json()

    # 2. User 2 creates FOUND report
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Blue Water Bottle",
            "category": "Bottle",
            "description": "Found near library table",
            "report_type": "FOUND",
            "approximate_date": "2026-11-12",
            "location": "Library"
        },
        headers=auth_headers_user2
    ).json()

    # 3. User 1 files claim on found item linking their lost report
    claim_payload = {
        "report_id": found["id"],
        "lost_report_id": lost["id"],
        "verification_details": "There is a small scratch near the neck and a barcode sticker on bottom"
    }
    claim_res = client.post("/api/v1/claims", json=claim_payload, headers=auth_headers_user1)
    assert claim_res.status_code == status.HTTP_201_CREATED
    claim_data = claim_res.json()
    assert claim_data["report_id"] == found["id"]
    assert claim_data["lost_report_id"] == lost["id"]
    assert claim_data["status"] == "PENDING"
    assert claim_data["verification_details"] == claim_payload["verification_details"]


def test_claim_own_found_item_rejected(client, auth_headers_user1):
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Watch",
            "category": "Accessories",
            "description": "Casio watch found in gym",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Gym"
        },
        headers=auth_headers_user1
    ).json()

    # User 1 tries to claim their own found item
    res = client.post(
        "/api/v1/claims",
        json={
            "report_id": found["id"],
            "verification_details": "This is actually my watch"
        },
        headers=auth_headers_user1
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot submit a claim against an item you reported" in res.json()["message"]


def test_claim_lost_report_rejected(client, auth_headers_user1, auth_headers_user2):
    lost = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Wallet",
            "category": "Bags",
            "description": "Lost wallet",
            "report_type": "LOST",
            "approximate_date": "2026-11-15",
            "location": "Cafeteria"
        },
        headers=auth_headers_user1
    ).json()

    # User 2 tries to file claim against a LOST report
    res = client.post(
        "/api/v1/claims",
        json={
            "report_id": lost["id"],
            "verification_details": "I want to claim this lost report"
        },
        headers=auth_headers_user2
    )
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    assert "Claims can only be filed against FOUND" in res.json()["message"]


def test_duplicate_claim_prevention(client, auth_headers_user1, auth_headers_user2):
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Notebook",
            "category": "Books",
            "description": "Physics notes",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Room 201"
        },
        headers=auth_headers_user2
    ).json()

    # 1st claim
    res1 = client.post(
        "/api/v1/claims",
        json={"report_id": found["id"], "verification_details": "My name is written inside cover"},
        headers=auth_headers_user1
    )
    assert res1.status_code == status.HTTP_201_CREATED

    # 2nd duplicate claim
    res2 = client.post(
        "/api/v1/claims",
        json={"report_id": found["id"], "verification_details": "Duplicate claim attempt"},
        headers=auth_headers_user1
    )
    assert res2.status_code == status.HTTP_409_CONFLICT
    assert "already have an active pending claim" in res2.json()["message"]


def test_claim_with_other_users_lost_report_rejected(client, auth_headers_user1, auth_headers_user2):
    user1_lost = client.post(
        "/api/v1/reports",
        json={
            "item_name": "ID Card",
            "category": "ID & Cards",
            "description": "Alice ID card",
            "report_type": "LOST",
            "approximate_date": "2026-11-15",
            "location": "Gate"
        },
        headers=auth_headers_user1
    ).json()

    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "ID Card",
            "category": "ID & Cards",
            "description": "Found ID card",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Gate"
        },
        headers=auth_headers_user1
    ).json()

    # User 2 tries to link User 1's lost report to their claim
    res = client.post(
        "/api/v1/claims",
        json={
            "report_id": found["id"],
            "lost_report_id": user1_lost["id"],
            "verification_details": "Details here"
        },
        headers=auth_headers_user2
    )
    assert res.status_code == status.HTTP_403_FORBIDDEN
    assert "Linked lost report must belong to the claimant" in res.json()["message"]


def test_withdraw_claim(client, auth_headers_user1, auth_headers_user2):
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Key ring",
            "category": "Keys",
            "description": "Bike key with Honda logo",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Parking"
        },
        headers=auth_headers_user2
    ).json()

    claim = client.post(
        "/api/v1/claims",
        json={"report_id": found["id"], "verification_details": "Small red ribbon attached"},
        headers=auth_headers_user1
    ).json()

    # User 1 withdraws claim
    withdraw_res = client.post(f"/api/v1/claims/{claim['id']}/withdraw", headers=auth_headers_user1)
    assert withdraw_res.status_code == status.HTTP_200_OK
    assert withdraw_res.json()["status"] == "WITHDRAWN"

    # Cannot withdraw again
    repeat_res = client.post(f"/api/v1/claims/{claim['id']}/withdraw", headers=auth_headers_user1)
    assert repeat_res.status_code == status.HTTP_400_BAD_REQUEST


def test_holder_can_view_and_third_party_cannot(client, auth_headers_user1, auth_headers_user2, user1):
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Jacket",
            "category": "Clothing",
            "description": "Denim jacket left on chair",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Auditorium"
        },
        headers=auth_headers_user1
    ).json()

    claim = client.post(
        "/api/v1/claims",
        json={"report_id": found["id"], "verification_details": "Secret pocket inside with 50 rupees"},
        headers=auth_headers_user2
    ).json()

    # Found-item holder (user1) can view — needed to approve/reject pickup
    view_res = client.get(f"/api/v1/claims/{claim['id']}", headers=auth_headers_user1)
    assert view_res.status_code == status.HTTP_200_OK

    # Unrelated third user cannot view
    reg = client.post(
        "/api/v1/auth/register",
        json={"name": "Third Party", "email": "third@campus.edu", "password": "Password123"},
    )
    assert reg.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "third@campus.edu", "password": "Password123"},
    )
    third_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    denied = client.get(f"/api/v1/claims/{claim['id']}", headers=third_headers)
    assert denied.status_code == status.HTTP_403_FORBIDDEN

