"""Test fixtures for the Todo backend test suite.

CRITICAL: Environment variables MUST be set before any app imports.
The app modules (db.py, config.py, auth.py) read env vars at import time.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["BETTER_AUTH_SECRET"] = "test-secret-minimum-32-characters-long"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

import jwt
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta

from httpx import AsyncClient, ASGITransport
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy import Column, String, Table, text

# ---------------------------------------------------------------------------
# Test engine + minimal user table for FK constraint
# ---------------------------------------------------------------------------

TEST_ENGINE = create_engine("sqlite://", echo=False)

user_table = Table(
    "user",
    SQLModel.metadata,
    Column("id", String, primary_key=True),
    extend_existing=True,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEST_SECRET = "test-secret-minimum-32-characters-long"
TEST_USER_ID = "test-user-123"
OTHER_USER_ID = "other-user-456"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def create_test_token(
    user_id: str = TEST_USER_ID,
    secret: str = TEST_SECRET,
    expired: bool = False,
) -> str:
    """Generate a JWT token for testing."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": f"{user_id}@test.com",
        "name": "Test User",
        "iat": now,
        "exp": now + timedelta(hours=-1 if expired else 1),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def auth_headers(user_id: str = TEST_USER_ID) -> dict:
    """Return Authorization headers with a valid test JWT."""
    token = create_test_token(user_id=user_id)
    return {"Authorization": f"Bearer {token}"}


def seed_test_user(session: Session, user_id: str = TEST_USER_ID) -> None:
    """Insert a test user row to satisfy FK constraints."""
    session.exec(text(f"INSERT OR IGNORE INTO user (id) VALUES ('{user_id}')"))
    session.commit()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(name="session")
def session_fixture():
    """Provide a fresh database session with tables created/dropped per test."""
    SQLModel.metadata.create_all(TEST_ENGINE)
    with Session(TEST_ENGINE) as session:
        yield session
    SQLModel.metadata.drop_all(TEST_ENGINE)


@pytest_asyncio.fixture(name="client")
async def client_fixture(session):
    """Provide an httpx AsyncClient wired to the FastAPI app with test DB."""
    from app.main import app
    from app.db import get_session

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()
