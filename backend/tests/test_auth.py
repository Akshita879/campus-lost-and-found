from fastapi import status


def test_register_user_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Charlie Chaplin",
            "email": "charlie@campus.edu",
            "password": "StrongPassword123"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Charlie Chaplin"
    assert data["email"] == "charlie@campus.edu"
    assert "id" in data
    assert "password_hash" not in data


def test_register_duplicate_email(client, user1):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice Duplicate",
            "email": user1.email,
            "password": "Password123"
        }
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in response.json()["message"]


def test_register_invalid_data(client):
    # Invalid email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Bad",
            "email": "not-an-email",
            "password": "Password123"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Password too short (< 8 chars)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Short",
            "email": "short@campus.edu",
            "password": "123"
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, user1):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "alice@campus.edu",
            "password": "Password123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alice@campus.edu"


def test_login_invalid_password(client, user1):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "alice@campus.edu",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect email or password" in response.json()["message"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@campus.edu",
            "password": "SomePassword123"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_authenticated(client, auth_headers_user1, user1):
    response = client.get("/api/v1/auth/me", headers=auth_headers_user1)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == user1.id
    assert data["email"] == user1.email


def test_get_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_invalid_token(client):
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
