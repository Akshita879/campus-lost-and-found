import io
from fastapi import status


def test_create_lost_report(client, auth_headers_user1):
    payload = {
        "item_name": "Blue Milton Water Bottle",
        "category": "Bottle",
        "description": "750ml blue metallic water bottle with black cap",
        "report_type": "LOST",
        "approximate_date": "2026-11-12",
        "location": "Central Library 2nd Floor"
    }
    response = client.post("/api/v1/reports", json=payload, headers=auth_headers_user1)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["item_name"] == payload["item_name"]
    assert data["report_type"] == "LOST"
    assert data["status"] == "ACTIVE"
    assert "id" in data
    assert "email" not in data  # Privacy check


def test_create_found_report(client, auth_headers_user2):
    payload = {
        "item_name": "Scientific Calculator Casio fx-991EX",
        "category": "Electronics",
        "description": "Black calculator found on desk in Room 302",
        "report_type": "FOUND",
        "approximate_date": "2026-11-14",
        "location": "Science Block Room 302"
    }
    response = client.post("/api/v1/reports", json=payload, headers=auth_headers_user2)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["report_type"] == "FOUND"
    assert data["status"] == "ACTIVE"


def test_create_report_with_image_upload(client, auth_headers_user1):
    image_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    files = {"image": ("test.png", io.BytesIO(image_content), "image/png")}
    data = {
        "item_name": "Silver Laptop Charger",
        "category": "Electronics",
        "description": "65W USB-C charger left on desk",
        "report_type": "FOUND",
        "approximate_date": "2026-11-15",
        "location": "Cafeteria"
    }
    response = client.post("/api/v1/reports/upload", data=data, files=files, headers=auth_headers_user1)
    assert response.status_code == status.HTTP_201_CREATED
    res_data = response.json()
    assert res_data["image_path"] is not None
    assert res_data["image_path"].startswith("uploads/")


def test_create_report_invalid_image_type(client, auth_headers_user1):
    bad_file = {"image": ("malicious.exe", io.BytesIO(b"MZ123"), "application/x-dosexec")}
    data = {
        "item_name": "Fake Item",
        "category": "Other",
        "description": "Testing invalid file",
        "report_type": "LOST",
        "approximate_date": "2026-11-15",
        "location": "Hall"
    }
    response = client.post("/api/v1/reports/upload", data=data, files=bad_file, headers=auth_headers_user1)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported file extension" in response.json()["message"]


def test_get_report_by_id(client, auth_headers_user1):
    create_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Black Backpack",
            "category": "Bags",
            "description": "Wildcraft backpack with notebooks",
            "report_type": "LOST",
            "approximate_date": "2026-11-10",
            "location": "Auditorium"
        },
        headers=auth_headers_user1
    )
    report_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/reports/{report_id}")
    assert get_res.status_code == status.HTTP_200_OK
    assert get_res.json()["item_name"] == "Black Backpack"


def test_update_own_report(client, auth_headers_user1):
    create_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "House Keys",
            "category": "Keys",
            "description": "3 keys on a red keychain",
            "report_type": "LOST",
            "approximate_date": "2026-11-11",
            "location": "Gym"
        },
        headers=auth_headers_user1
    )
    report_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/reports/{report_id}",
        json={"description": "3 keys on a red keychain with an Eiffel tower tag"},
        headers=auth_headers_user1
    )
    assert update_res.status_code == status.HTTP_200_OK
    assert "Eiffel tower tag" in update_res.json()["description"]


def test_update_other_user_report_forbidden(client, auth_headers_user1, auth_headers_user2):
    # User 1 creates report
    create_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Student ID Card",
            "category": "ID & Cards",
            "description": "Lost student ID card",
            "report_type": "LOST",
            "approximate_date": "2026-11-13",
            "location": "Main Gate"
        },
        headers=auth_headers_user1
    )
    report_id = create_res.json()["id"]

    # User 2 tries to update User 1's report
    update_res = client.put(
        f"/api/v1/reports/{report_id}",
        json={"item_name": "Hacked ID"},
        headers=auth_headers_user2
    )
    assert update_res.status_code == status.HTTP_403_FORBIDDEN


def test_close_own_report(client, auth_headers_user1):
    create_res = client.post(
        "/api/v1/reports",
        json={
            "item_name": "Blue Umbrella",
            "category": "Accessories",
            "description": "Small foldable blue umbrella",
            "report_type": "LOST",
            "approximate_date": "2026-11-14",
            "location": "Canteen"
        },
        headers=auth_headers_user1
    )
    report_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/reports/{report_id}", headers=auth_headers_user1)
    assert delete_res.status_code == status.HTTP_200_OK
    assert delete_res.json()["status"] == "CLOSED"


def test_get_my_reports(client, auth_headers_user1):
    client.post(
        "/api/v1/reports",
        json={
            "item_name": "My Lost Pen",
            "category": "Stationery",
            "description": "Parker pen",
            "report_type": "LOST",
            "approximate_date": "2026-11-14",
            "location": "Lab 1"
        },
        headers=auth_headers_user1
    )
    res = client.get("/api/v1/reports/my", headers=auth_headers_user1)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.json()) >= 1
