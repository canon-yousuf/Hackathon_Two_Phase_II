"""Service layer unit tests (FR-039 through FR-045).

Tests call service functions directly with a SQLModel Session,
verifying business logic in isolation (no HTTP).
"""

import time
import pytest
from tests.conftest import TEST_USER_ID, OTHER_USER_ID, seed_test_user
from app.models.task import TaskCreate, TaskUpdate
from app.services.task_service import (
    get_tasks,
    get_task,
    create_task,
    update_task,
    delete_task,
    toggle_complete,
)


def test_get_tasks_filters_by_user_id(session):
    """FR-039: Task retrieval filters by user_id correctly."""
    seed_test_user(session, TEST_USER_ID)
    seed_test_user(session, OTHER_USER_ID)

    create_task(session, TEST_USER_ID, TaskCreate(title="Mine"))
    create_task(session, OTHER_USER_ID, TaskCreate(title="Theirs"))

    my_tasks = get_tasks(session, TEST_USER_ID)
    assert len(my_tasks) == 1
    assert my_tasks[0].title == "Mine"


def test_get_tasks_filters_by_status(session):
    """FR-040: Task retrieval filters by status correctly."""
    seed_test_user(session, TEST_USER_ID)

    create_task(session, TEST_USER_ID, TaskCreate(title="Pending"))
    task2 = create_task(session, TEST_USER_ID, TaskCreate(title="Done"))
    toggle_complete(session, TEST_USER_ID, task2.id)

    pending = get_tasks(session, TEST_USER_ID, status="pending")
    assert len(pending) == 1
    assert pending[0].title == "Pending"

    completed = get_tasks(session, TEST_USER_ID, status="completed")
    assert len(completed) == 1
    assert completed[0].title == "Done"


def test_get_tasks_sorts_correctly(session):
    """FR-041: Task retrieval sorts correctly."""
    seed_test_user(session, TEST_USER_ID)

    create_task(session, TEST_USER_ID, TaskCreate(title="Banana"))
    time.sleep(0.05)
    create_task(session, TEST_USER_ID, TaskCreate(title="Apple"))

    # Sort by title → alphabetical
    by_title = get_tasks(session, TEST_USER_ID, sort="title")
    assert by_title[0].title == "Apple"
    assert by_title[1].title == "Banana"

    # Sort by created → newest first
    by_created = get_tasks(session, TEST_USER_ID, sort="created")
    assert by_created[0].title == "Apple"
    assert by_created[1].title == "Banana"


def test_create_task_defaults(session):
    """FR-042: create_task sets correct defaults (completed=False, timestamps)."""
    seed_test_user(session, TEST_USER_ID)

    task = create_task(session, TEST_USER_ID, TaskCreate(title="Defaults"))
    assert task.completed is False
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.user_id == TEST_USER_ID


def test_update_task_partial(session):
    """FR-043: update_task modifies only the provided fields."""
    seed_test_user(session, TEST_USER_ID)

    task = create_task(
        session, TEST_USER_ID,
        TaskCreate(title="Original", description="Keep me"),
    )

    updated = update_task(
        session, TEST_USER_ID, task.id,
        TaskUpdate(title="Changed"),
        {"title"},
    )
    assert updated is not None
    assert updated.title == "Changed"
    assert updated.description == "Keep me"


def test_delete_task_returns_bool(session):
    """FR-044: delete_task returns True for existing, False for non-existent."""
    seed_test_user(session, TEST_USER_ID)

    task = create_task(session, TEST_USER_ID, TaskCreate(title="Deletable"))
    assert delete_task(session, TEST_USER_ID, task.id) is True
    assert delete_task(session, TEST_USER_ID, 99999) is False


def test_toggle_complete_flips(session):
    """FR-045: toggle_complete flips the completed boolean."""
    seed_test_user(session, TEST_USER_ID)

    task = create_task(session, TEST_USER_ID, TaskCreate(title="Flipper"))
    assert task.completed is False

    toggled = toggle_complete(session, TEST_USER_ID, task.id)
    assert toggled is not None
    assert toggled.completed is True

    toggled_back = toggle_complete(session, TEST_USER_ID, task.id)
    assert toggled_back is not None
    assert toggled_back.completed is False
