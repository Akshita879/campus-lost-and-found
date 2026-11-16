from fastapi import status


def seed_test_reports(client, auth_headers):
    reports = [
        {"item_name": "Apple AirPods Pro", "category": "Electronics", "description": "White case with right pod missing", "report_type": "LOST", "approximate_date": "2026-11-10", "location": "Library"},
        {"item_name": "Samsung Galaxy Buds", "category": "Electronics", "description": "Black wireless earphones", "report_type": "FOUND", "approximate_date": "2026-11-11", "location": "Library"},
        {"item_name": "Mathematics Textbook", "category": "Books", "description": "Calculus 9th edition by Stewart", "report_type": "LOST", "approximate_date": "2026-11-12", "location": "Science Block"},
        {"item_name": "Organic Chemistry Book", "category": "Books", "description": "Chemistry notebook with blue cover", "report_type": "FOUND", "approximate_date": "2026-11-12", "location": "Chemistry Lab"},
        {"item_name": "Stainless Steel Bottle", "category": "Bottle", "description": "Silver hydro flask bottle", "report_type": "LOST", "approximate_date": "2026-11-13", "location": "Gymnasium"},
    ]
    for r in reports:
        client.post("/api/v1/reports", json=r, headers=auth_headers)


def test_search_by_keyword(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?keyword=AirPods")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] >= 1
    assert any("AirPods" in item["item_name"] for item in data["items"])


def test_search_filter_by_category(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?category=Electronics")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["category"] == "Electronics" for item in data["items"])


def test_search_filter_by_report_type(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?report_type=FOUND")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(item["report_type"] == "FOUND" for item in data["items"])


def test_search_combined_filters(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?category=Electronics&location=Library&report_type=FOUND")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["item_name"] == "Samsung Galaxy Buds"


def test_search_date_range(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?date_from=2026-11-11&date_to=2026-11-12")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for item in data["items"]:
        assert "2026-11-11" <= item["approximate_date"] <= "2026-11-12"


def test_search_pagination(client, auth_headers_user1):
    seed_test_reports(client, auth_headers_user1)

    response = client.get("/api/v1/reports/search?page=1&page_size=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["total_pages"] >= 3
