from fastapi import status


def test_matching_exact_and_fuzzy_pair(client, auth_headers_user1, auth_headers_user2):
    # 1. User 1 posts LOST report
    lost_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Blue Milton Water Bottle",
            "category": "Bottle",
            "description": "750ml blue Milton bottle with a black cap and gym sticker",
            "report_type": "LOST",
            "approximate_date": "2026-11-12",
            "location": "Central Library"
        },
        headers=auth_headers_user1
    )
    lost_id = lost_res.json()["id"]

    # 2. User 2 posts matching FOUND report
    found_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Blue Milton Bottle",
            "category": "Bottle",
            "description": "Blue bottle with black cap found near study desk",
            "report_type": "FOUND",
            "approximate_date": "2026-11-12",
            "location": "Central Library"
        },
        headers=auth_headers_user2
    )
    found_id = found_res.json()["id"]

    # 3. User 2 posts another unrelated FOUND report
    client.post(
        "/api/v1/reports",
        json={
            "item_name": "Leather Wallet",
            "category": "Bags & Wallets",
            "description": "Brown leather wallet with currency notes",
            "report_type": "FOUND",
            "approximate_date": "2026-11-01",
            "location": "Sports Ground"
        },
        headers=auth_headers_user2
    )

    # 4. Fetch matches for LOST report
    match_res = client.get(f"/api/v1/reports/{lost_id}/matches", headers=auth_headers_user1)
    assert match_res.status_code == status.HTTP_200_OK
    data = match_res.json()
    assert data["lost_report_id"] == lost_id
    matches = data["matches"]
    assert len(matches) >= 1

    top_match = matches[0]
    assert top_match["found_report_id"] == found_id
    assert top_match["similarity_score"] >= 80.0
    assert top_match["score_breakdown"]["category"] == 100.0
    assert top_match["score_breakdown"]["date"] == 100.0
    assert top_match["score_breakdown"]["location"] == 100.0
    assert top_match["score_breakdown"]["item_name"] >= 90.0


def test_matching_does_not_compare_lost_with_lost(client, auth_headers_user1, auth_headers_user2):
    # Lost report 1
    lost1 = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Scientific Calculator",
            "category": "Electronics",
            "description": "Casio fx-991EX",
            "report_type": "LOST",
            "approximate_date": "2026-11-14",
            "location": "Room 101"
        },
        headers=auth_headers_user1
    ).json()

    # Lost report 2 (identical details, but LOST)
    client.post(
        "/api/v1/reports",
        json={
            "item_name": "Scientific Calculator",
            "category": "Electronics",
            "description": "Casio fx-991EX",
            "report_type": "LOST",
            "approximate_date": "2026-11-14",
            "location": "Room 101"
        },
        headers=auth_headers_user2
    )

    # Verify no match returned because both are LOST
    res = client.get(f"/api/v1/reports/{lost1['id']}/matches", headers=auth_headers_user1)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()["matches"]) == 0


def test_matching_excludes_closed_and_resolved(client, auth_headers_user1, auth_headers_user2):
    lost = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Sony Headphones",
            "category": "Electronics",
            "description": "Black over-ear headphones",
            "report_type": "LOST",
            "approximate_date": "2026-11-15",
            "location": "Cafeteria"
        },
        headers=auth_headers_user1
    ).json()

    # Found report that gets CLOSED
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Sony Headphones",
            "category": "Electronics",
            "description": "Black over-ear headphones found on table",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Cafeteria"
        },
        headers=auth_headers_user2
    ).json()

    # Close found report
    client.delete(f"/api/v1/reports/{found['id']}", headers=auth_headers_user2)

    # Check matches
    res = client.get(f"/api/v1/reports/{lost['id']}/matches", headers=auth_headers_user1)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()["matches"]) == 0


def test_matching_called_on_found_report_rejected(client, auth_headers_user1):
    found = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Keys",
            "category": "Keys",
            "description": "Silver key",
            "report_type": "FOUND",
            "approximate_date": "2026-11-15",
            "location": "Gate"
        },
        headers=auth_headers_user1
    ).json()

    res = client.get(f"/api/v1/reports/{found['id']}/matches", headers=auth_headers_user1)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
