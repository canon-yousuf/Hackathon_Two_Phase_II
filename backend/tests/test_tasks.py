"""Task CRUD endpoint tests (FR-007 through FR-038).

Tests verify all 6 REST endpoints return correct status codes,
response bodies, and enforce user isolation.
"""

import time
import pytest
from tests.conftest import (
    TEST_USER_ID,
    OTHER_USER_ID,
    auth_headers,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


async def create_task_for_user(
    client, user_id=TEST_USER_ID, title="Test Task", description=None
):
    """POST a new task and return the response JSON."""
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    response = await client.post(
        f"/api/{user_id}/tasks",
        json=payload,
        headers=auth_headers(user_id),
    )
    assert response.status_code == 201
    return response.json()


# ===========================================================================
# GET /api/{user_id}/tasks — List (FR-007 through FR-015)
# ===========================================================================


@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    """FR-007: Empty array returned when a user has no tasks."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_tasks_user_isolation(client):
    """FR-008: Only tasks belonging to the authenticated user are returned."""
    await create_task_for_user(client, TEST_USER_ID, "My Task")
    await create_task_for_user(client, OTHER_USER_ID, "Other Task")

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers=auth_headers(TEST_USER_ID),
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "My Task"


@pytest.mark.asyncio
async def test_list_tasks_filter_pending(client):
    """FR-009: Filtering by pending returns only incomplete tasks."""
    task = await create_task_for_user(client, title="Pending Task")
    await create_task_for_user(client, title="Completed Task")
    # Toggle second task to completed
    await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task['id'] + 1}/complete",
        headers=auth_headers(),
    )

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?status=pending",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is False


@pytest.mark.asyncio
async def test_list_tasks_filter_completed(client):
    """FR-010: Filtering by completed returns only completed tasks."""
    await create_task_for_user(client, title="Pending Task")
    task2 = await create_task_for_user(client, title="Completed Task")
    await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task2['id']}/complete",
        headers=auth_headers(),
    )

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?status=completed",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["completed"] is True


@pytest.mark.asyncio
async def test_list_tasks_filter_all(client):
    """FR-011: Filtering by 'all' returns all tasks."""
    await create_task_for_user(client, title="Task A")
    task2 = await create_task_for_user(client, title="Task B")
    await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task2['id']}/complete",
        headers=auth_headers(),
    )

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?status=all",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_list_tasks_sort_created(client):
    """FR-012: Sorting by creation date returns newest first."""
    await create_task_for_user(client, title="First")
    time.sleep(0.05)  # Ensure different timestamps
    await create_task_for_user(client, title="Second")

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?sort=created",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 2
    assert tasks[0]["title"] == "Second"
    assert tasks[1]["title"] == "First"


@pytest.mark.asyncio
async def test_list_tasks_sort_title(client):
    """FR-013: Sorting by title returns alphabetical order."""
    await create_task_for_user(client, title="Banana")
    await create_task_for_user(client, title="Apple")

    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?sort=title",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["title"] == "Apple"
    assert tasks[1]["title"] == "Banana"


@pytest.mark.asyncio
async def test_list_tasks_invalid_status(client):
    """FR-014: Invalid status filter returns 422."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?status=invalid",
        headers=auth_headers(),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks_invalid_sort(client):
    """FR-015: Invalid sort value returns 422."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks?sort=invalid",
        headers=auth_headers(),
    )
    assert response.status_code == 422


# ===========================================================================
# POST /api/{user_id}/tasks — Create (FR-016 through FR-022)
# ===========================================================================


@pytest.mark.asyncio
async def test_create_task_valid_title(client):
    """FR-016: Valid title creates a task and returns 201."""
    response = await client.post(
        f"/api/{TEST_USER_ID}/tasks",
        json={"title": "New Task"},
        headers=auth_headers(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Task"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_task_with_description(client):
    """FR-017: Valid title with description creates a task and returns 201."""
    response = await client.post(
        f"/api/{TEST_USER_ID}/tasks",
        json={"title": "Task", "description": "Details here"},
        headers=auth_headers(),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Details here"


@pytest.mark.asyncio
async def test_create_task_empty_title(client):
    """FR-018: Empty title returns 422."""
    response = await client.post(
        f"/api/{TEST_USER_ID}/tasks",
        json={"title": ""},
        headers=auth_headers(),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_missing_title(client):
    """FR-019: Missing title field returns 422."""
    response = await client.post(
        f"/api/{TEST_USER_ID}/tasks",
        json={},
        headers=auth_headers(),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_title_too_long(client):
    """FR-020: Title over 200 characters returns 422."""
    response = await client.post(
        f"/api/{TEST_USER_ID}/tasks",
        json={"title": "x" * 201},
        headers=auth_headers(),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_task_default_incomplete(client):
    """FR-021: Created task has completed=false by default."""
    task = await create_task_for_user(client, title="Fresh Task")
    assert task["completed"] is False


@pytest.mark.asyncio
async def test_create_task_correct_user_id(client):
    """FR-022: Created task user_id matches the authenticated user."""
    task = await create_task_for_user(client, title="My Task")
    assert task["user_id"] == TEST_USER_ID


# ===========================================================================
# GET /api/{user_id}/tasks/{id} — Get Single (FR-023 through FR-025)
# ===========================================================================


@pytest.mark.asyncio
async def test_get_task_found(client):
    """FR-023: Valid task identifier returns 200 with task data."""
    task = await create_task_for_user(client, title="Findable")
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Findable"


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    """FR-024: Non-existent task identifier returns 404."""
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks/99999",
        headers=auth_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_other_user(client):
    """FR-025: Task belonging to another user returns 404 (not 403)."""
    task = await create_task_for_user(client, OTHER_USER_ID, "Other's Task")
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        headers=auth_headers(TEST_USER_ID),
    )
    assert response.status_code == 404


# ===========================================================================
# PUT /api/{user_id}/tasks/{id} — Update (FR-026 through FR-031)
# ===========================================================================


@pytest.mark.asyncio
async def test_update_task_title_only(client):
    """FR-026: Updating title only returns 200 with updated title."""
    task = await create_task_for_user(client, title="Original")
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        json={"title": "Updated Title"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_update_task_description_only(client):
    """FR-027: Updating description only returns 200."""
    task = await create_task_for_user(client, title="Keep Title")
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        json={"description": "New Description"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "New Description"
    assert data["title"] == "Keep Title"


@pytest.mark.asyncio
async def test_update_task_both_fields(client):
    """FR-028: Updating both title and description returns 200."""
    task = await create_task_for_user(client, title="Old")
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        json={"title": "New Title", "description": "New Desc"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New Desc"


@pytest.mark.asyncio
async def test_update_task_timestamp_changes(client):
    """FR-029: updated_at changes after an update."""
    task = await create_task_for_user(client, title="Timestamped")
    original_updated = task["updated_at"]
    time.sleep(0.05)
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        json={"title": "Changed"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["updated_at"] != original_updated


@pytest.mark.asyncio
async def test_update_task_not_found(client):
    """FR-030: Updating a non-existent task returns 404."""
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/99999",
        json={"title": "Ghost"},
        headers=auth_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_task_empty_title(client):
    """FR-031: Updating with an empty title returns 422."""
    task = await create_task_for_user(client, title="Valid")
    response = await client.put(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        json={"title": ""},
        headers=auth_headers(),
    )
    assert response.status_code == 422


# ===========================================================================
# DELETE /api/{user_id}/tasks/{id} (FR-032 through FR-034)
# ===========================================================================


@pytest.mark.asyncio
async def test_delete_task_success(client):
    """FR-032: Deleting a valid task returns 204 with no body."""
    task = await create_task_for_user(client, title="Delete Me")
    response = await client.delete(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        headers=auth_headers(),
    )
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.asyncio
async def test_delete_task_not_found(client):
    """FR-033: Deleting a non-existent task returns 404."""
    response = await client.delete(
        f"/api/{TEST_USER_ID}/tasks/99999",
        headers=auth_headers(),
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_no_longer_in_list(client):
    """FR-034: Deleted task no longer appears in the list."""
    task = await create_task_for_user(client, title="Vanish")
    await client.delete(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}",
        headers=auth_headers(),
    )
    response = await client.get(
        f"/api/{TEST_USER_ID}/tasks",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert "Vanish" not in titles


# ===========================================================================
# PATCH /api/{user_id}/tasks/{id}/complete — Toggle (FR-035 through FR-038)
# ===========================================================================


@pytest.mark.asyncio
async def test_toggle_pending_to_completed(client):
    """FR-035: Toggling a pending task makes it completed."""
    task = await create_task_for_user(client, title="Toggle Me")
    assert task["completed"] is False

    response = await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}/complete",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["completed"] is True


@pytest.mark.asyncio
async def test_toggle_completed_to_pending(client):
    """FR-036: Toggling a completed task makes it pending."""
    task = await create_task_for_user(client, title="Toggle Twice")
    # First toggle: pending → completed
    await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}/complete",
        headers=auth_headers(),
    )
    # Second toggle: completed → pending
    response = await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}/complete",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["completed"] is False


@pytest.mark.asyncio
async def test_toggle_timestamp_changes(client):
    """FR-037: updated_at changes after a toggle."""
    task = await create_task_for_user(client, title="Timestamp Toggle")
    original_updated = task["updated_at"]
    time.sleep(0.05)
    response = await client.patch(
        f"/api/{TEST_USER_ID}/tasks/{task['id']}/complete",
        headers=auth_headers(),
    )
    assert response.status_code == 200
    assert response.json()["updated_at"] != original_updated


@pytest.mark.asyncio
async def test_toggle_not_found(client):
    """FR-038: Toggling a non-existent task returns 404."""
    response = await client.patch(
        f"/api/{TEST_USER_ID}/tasks/99999/complete",
        headers=auth_headers(),
    )
    assert response.status_code == 404
