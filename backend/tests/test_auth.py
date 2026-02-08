"""Authentication middleware tests (FR-001 through FR-006).

Tests verify the backend correctly rejects unauthorized requests
and allows valid authenticated requests.
"""

import pytest
from tests.conftest import (
    TEST_USER_ID,
    OTHER_USER_ID,
    create_test_token,
    auth_headers,
)


@pytest.mark.asyncio
async def test_no_token_returns_401(client):
    """FR-001: Request with no authorization credentials is rejected."""
    response = await client.get(f"/api/{TEST_USER_ID}/tasks")
    # FastAPI's HTTPBearer returns 403 when no credentials are provided
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_malformed_token_returns_401(client):
    """FR-002: Request with a malformed credential returns 401."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers={"Authorization": "Bearer not-a-valid-jwt"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_expired_token_returns_401(client):
    """FR-003: Request with an expired credential returns 401."""
    token = create_test_token(expired=True)
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_wrong_secret_returns_401(client):
    """FR-004: Request with a credential signed by the wrong secret returns 401."""
    token = create_test_token(secret="wrong-secret-key-that-is-32-chars-long")
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_id_mismatch_returns_403(client):
    """FR-005: Valid credential but URL user_id doesn't match returns 403."""
    # Token is for TEST_USER_ID, but URL has OTHER_USER_ID
    response = await client.get(
        f"/api/{OTHER_USER_ID}/tasks",
        headers=auth_headers(TEST_USER_ID),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_token_missing_sub_returns_401(client):
    """Token with no 'sub' claim is rejected."""
    import jwt as pyjwt
    from tests.conftest import TEST_SECRET

    token = pyjwt.encode(
        {"email": "no-sub@test.com"},
        TEST_SECRET,
        algorithm="HS256",
    )
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_valid_token_matching_user_returns_200(client):
    """FR-006: Valid credential with matching user_id returns 200."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers=auth_headers(TEST_USER_ID),
    )
    assert response.status_code == 200
