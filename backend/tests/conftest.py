import os
import sys
from pathlib import Path
import email_validator
import pytest

email_validator.CHECK_DELIVERABILITY = False
email_validator.TEST_ENVIRONMENT = True
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.database import Base, get_db
from app.main import app
from app.models.user import User
from app.utils.security import hash_password, create_access_token

# Test database: In-memory SQLite with StaticPool for thread-safe in-memory sharing
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test function."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient wired to the test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def user1(db_session) -> User:
    """Pre-seeded user 1."""
    user = User(
        name="Alice Student",
        email="alice@campus.edu",
        password_hash=hash_password("Password123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def user2(db_session) -> User:
    """Pre-seeded user 2."""
    user = User(
        name="Bob Staff",
        email="bob@campus.edu",
        password_hash=hash_password("Secret12345")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers_user1(user1) -> dict:
    """Authorization headers for user 1."""
    token = create_access_token(subject=user1.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_user2(user2) -> dict:
    """Authorization headers for user 2."""
    token = create_access_token(subject=user2.id)
    return {"Authorization": f"Bearer {token}"}
